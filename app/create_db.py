import sqlite3
import pandas as pd
import os
import sys

def create_database():
    # Define paths - using absolute paths for clarity
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(base_dir, 'data')
    db_path = os.path.join(base_dir, 'weather_data.db')

    print(f"Database will be created at: {db_path}")
    print(f"Using data from: {data_dir}")

    # Verify CSV files exist AND are readable
    required_files = ['county_averages.csv', 'city_county_mapping.csv']
    for f in required_files:
        filepath = os.path.join(data_dir, f)
        if not os.path.exists(filepath):
            print(f"Error: Missing file {filepath}", file=sys.stderr)
            sys.exit(1)
        if not os.access(filepath, os.R_OK):
            print(f"Error: Cannot read file {filepath}", file=sys.stderr)
            sys.exit(1)

    conn = None  # Initialize connection variable
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Test if we can create/write to the DB location
        with open(db_path, 'w') as test_file:
            test_file.write("")  # Creates empty file if permissions allow

        # Connect to database with explicit timeout
        conn = sqlite3.connect(db_path, timeout=30)
        print("Successfully connected to database")

        # Load data with explicit error checking
        try:
            averages = pd.read_csv(os.path.join(data_dir, 'county_averages.csv'))
            print("Successfully loaded county averages data")
            averages.to_sql('county_averages', conn, if_exists='replace', index=False)
            print("Successfully wrote county averages to database")

            cities = pd.read_csv(os.path.join(data_dir, 'city_county_mapping.csv'))
            print("Successfully loaded city/county mapping data")
            cities.to_sql('city_county', conn, if_exists='replace', index=False)
            print("Successfully wrote city/county data to database")

            # Create indexes with explicit commits
            conn.execute('CREATE INDEX IF NOT EXISTS idx_city_state ON city_county(primary_city, state)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_county_month ON county_averages(st_abb, county_name, month)')
            conn.commit()
            print("Indexes created successfully")

        except pd.errors.EmptyDataError as e:
            print(f"Error: CSV file is empty or corrupt: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error processing data: {str(e)}", file=sys.stderr)
            sys.exit(1)

    except PermissionError as pe:
        print(f"Permission denied: {pe}", file=sys.stderr)
        print(f"Try running: chmod 775 {os.path.dirname(db_path)}", file=sys.stderr)
        sys.exit(1)
    except sqlite3.Error as sqle:
        print(f"SQLite error: {sqle}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

        # Set permissions (if on Unix-like system)
        if os.name != 'nt' and os.path.exists(db_path):
            try:
                os.chmod(db_path, 0o666)
                print(f"Set permissions on {db_path} to 0666")
            except Exception as e:
                print(f"Warning: Could not set permissions: {e}")

if __name__ == '__main__':
    create_database()
