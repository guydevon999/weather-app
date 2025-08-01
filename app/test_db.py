import sqlite3
db_path = "/home/dguy/containers/weather-app/test.db"
try:
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE test (id INTEGER);")
    conn.close()
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
