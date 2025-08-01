import sqlite3
import os
from datetime import datetime

# Add this state mapping dictionary
STATE_MAPPING = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
    'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
    'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
    'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
    'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
    'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
    'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
    'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
    'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
    'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
    'wisconsin': 'WI', 'wyoming': 'WY'
}

class WeatherDB:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'weather_data.db'
        )

    def execute(self, query, params=()):
        """Helper method to execute SQL queries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor

    def _normalize_state(self, state):
        """Convert state name to abbreviation if needed"""
        state = state.strip().lower()
        return STATE_MAPPING.get(state, state.upper())

    def get_county_for_city(self, city, state):
        """Returns county name for given city/state"""
        normalized_state = self._normalize_state(state)
        result = self.execute(
            "SELECT county FROM city_county WHERE primary_city = ? AND state = ?",
            (city, normalized_state)
        ).fetchone()
        return result[0] if result else None

    def get_monthly_average(self, state, county, month=None):
        """Returns historical average temp for county/month (or any month if None)"""
        try:
            normalized_state = self._normalize_state(state)
            query = """
                SELECT tavg_f FROM county_averages
                WHERE st_abb = ? AND county_name = ?
                """
            params = [normalized_state, county]

            if month is not None:
                query += " AND month = ?"
                params.append(month)
            else:
                query += " LIMIT 1"  # Get any month's data

            result = self.execute(query, params).fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Database error in get_monthly_average: {e}")
            return None
