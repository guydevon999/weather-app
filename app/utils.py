def get_weather_icon(icon_code):
    """Map OpenWeatherMap icon codes to Weather Icons classes"""
    icon_map = {
        '01d': 'day-sunny',
        '01n': 'night-clear',
        '02d': 'day-cloudy',
        '02n': 'night-alt-cloudy',
        '03d': 'cloud',
        '03n': 'cloud',
        '04d': 'cloudy',
        '04n': 'cloudy',
        '09d': 'rain',
        '09n': 'rain',
        '10d': 'day-rain',
        '10n': 'night-alt-rain',
        '11d': 'lightning',
        '11n': 'lightning',
        '13d': 'snow',
        '13n': 'snow',
        '50d': 'fog',
        '50n': 'fog'
    }
    return f"wi-{icon_map.get(icon_code, 'day-sunny')}"
