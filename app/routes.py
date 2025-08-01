import os
from datetime import datetime
from flask import Blueprint, render_template, request
import requests
from app.utils import get_weather_icon
from app.db_helper import WeatherDB

# Initialize the Blueprint
main_bp = Blueprint('main', __name__)

# Initialize the database helper
db = WeatherDB()

def create_forecast_structure():
    """Returns a guaranteed-safe forecast data structure"""
    return {
        'day_name': '',
        'time_periods': []
    }

def add_county_comparison(weather_info, city, state, unit='fahrenheit'):
    """
    Enhanced county temperature comparison with comprehensive debugging
    Returns weather_info with added county_comparison data if available
    """
    debug_info = []
    debug_info.append(f"\n[DEBUG] Starting comparison for: {city}, {state} (unit: {unit})")

    if not state or weather_info.get('temp') is None:
        debug_info.append("[DEBUG] Skipping - missing state or temperature data")
        weather_info['debug'] = "\n".join(debug_info)
        return weather_info

    try:
        debug_info.append("[DEBUG] Looking up county...")
        county = db.get_county_for_city(city, state)
        debug_info.append(f"[DEBUG] Found county: {county}")

        if not county:
            debug_info.append("[DEBUG] No county mapping found")
            weather_info['debug'] = "\n".join(debug_info)
            return weather_info

        current_month = datetime.now().month
        debug_info.append(f"[DEBUG] Checking month: {current_month}")

        # Try getting specific month data first
        avg_temp = db.get_monthly_average(state, county, current_month)
        debug_info.append(f"[DEBUG] Historical avg temp for month {current_month}: {avg_temp}")

        # Fallback to any month's data if no specific month found
        if avg_temp is None:
            debug_info.append("[DEBUG] Trying fallback to any monthly data...")
            avg_temp = db.get_monthly_average(state, county, None)
            debug_info.append(f"[DEBUG] Fallback avg temp: {avg_temp}")

        if avg_temp is not None:
            current_temp = weather_info['temp']
            debug_info.append(f"[DEBUG] Current temp: {current_temp}")

            # Convert units if needed
            if unit == 'celsius':
                avg_temp_celsius = (avg_temp - 32) * 5/9
                debug_info.append(f"[DEBUG] Converted {avg_temp}°F to {avg_temp_celsius}°C")
                avg_temp = avg_temp_celsius

            difference = current_temp - avg_temp
            weather_info['county_comparison'] = {
                'county': county,
                'historical_avg': round(avg_temp, 1),
                'difference': round(difference, 1),
                'difference_abs': round(abs(difference), 1),
                'is_higher': difference > 0,
                'unit': unit,
                'month': current_month if avg_temp else "annual"
            }
            debug_info.append("[DEBUG] Successfully added county comparison")
        else:
            debug_info.append("[DEBUG] No historical data found at all")

    except Exception as e:
        debug_info.append(f"[ERROR] County comparison failed: {str(e)}")

    # Add debug info to weather_info for template display
    weather_info['debug'] = "\n".join(debug_info)
    print("\n".join(debug_info))  # Also print to console

    return weather_info

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    # Default values
    city = request.form.get('city', 'New York').strip()
    state = request.form.get('state', '').strip().upper()
    country = request.form.get('country', 'US').upper().strip()
    unit = request.form.get('unit', 'fahrenheit')

    # Initialize weather data structure
    weather_info = {
        'city': city,
        'state': state,
        'country': country,
        'temp': None,
        'description': 'No data available',
        'icon': 'wi-na',
        'humidity': 0,
        'wind': 0.0,
        'unit': unit,
        'debug': ""
    }

    forecast_days = []
    error_msg = None

    try:
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            raise ValueError("OpenWeather API key not found")

        # Build location query
        location = f"{city},{state},{country}" if state else f"{city},{country}"

        # Current weather with timeout
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&units={'imperial' if unit == 'fahrenheit' else 'metric'}&appid={api_key}"
        current_response = requests.get(current_url, timeout=10)

        if current_response.status_code == 200:
            current_data = current_response.json()
            weather_info.update({
                'city': current_data.get('name', city),
                'temp': float(current_data['main']['temp']),
                'description': current_data['weather'][0]['description'].title(),
                'icon': get_weather_icon(current_data['weather'][0]['icon']),
                'humidity': current_data['main']['humidity'],
                'wind': current_data['wind']['speed'],
                'unit': unit
            })

            # Add county comparison for US locations
            if country == 'US' and state:
                weather_info = add_county_comparison(weather_info, city, state, unit)

        # Forecast data with timeout
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&units={'imperial' if unit == 'fahrenheit' else 'metric'}&appid={api_key}"
        forecast_response = requests.get(forecast_url, timeout=10)

        if forecast_response.status_code == 200:
            forecast_json = forecast_response.json()
            if forecast_json.get('list'):
                daily_data = {}
                for period in forecast_json['list'][:40]:  # Limit to 5 days
                    try:
                        dt = datetime.fromtimestamp(period['dt'])
                        date = dt.strftime('%Y-%m-%d')

                        if date not in daily_data:
                            daily_data[date] = create_forecast_structure()
                            daily_data[date]['day_name'] = dt.strftime('%A')

                        daily_data[date]['time_periods'].append({
                            'time': dt.strftime('%H:%M'),
                            'temp': float(period['main']['temp']),
                            'humidity': int(period['main']['humidity']),
                            'description': str(period['weather'][0]['description']).title(),
                            'icon': get_weather_icon(period['weather'][0]['icon']),
                            'unit': unit
                        })
                    except (KeyError, TypeError) as e:
                        continue

                forecast_days = list(daily_data.values())

    except requests.exceptions.RequestException as e:
        error_msg = "Weather service unavailable. Please try again later."
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"Application error: {str(e)}")

    return render_template(
        'index.html',
        weather=weather_info,
        forecast=forecast_days[:5],  # Only show 5 days max
        error=error_msg,
        unit=unit
    )
