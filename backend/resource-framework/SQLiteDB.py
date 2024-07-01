import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('climate_data.db')
cursor = conn.cursor()

# Create the weather_data table with the defined schema if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE,
        temperature_2m_max REAL,
        temperature_2m_min REAL,
        uv_index_max REAL,
        precipitation_sum REAL,
        rain_sum REAL,
        showers_sum REAL,
        snowfall_sum REAL,
        precipitation_probability_max REAL,
        soil_moisture_1_to_3cm REAL,
        soil_moisture_9_to_27cm REAL
    )
''')

# Create the metadata table for units if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS metadata (
        column_name TEXT PRIMARY KEY,
        unit TEXT
    )
''')

# Insert units into the metadata table
units = {
    "date": "YYYY-MM-DD",
    "temperature_2m_max": "°C",
    "temperature_2m_min": "°C",
    "uv_index_max": "index",
    "precipitation_sum": "mm",
    "rain_sum": "mm",
    "showers_sum": "mm",
    "snowfall_sum": "mm",
    "precipitation_probability_max": "%",
    "soil_moisture_1_to_3cm": "m³/m³",
    "soil_moisture_9_to_27cm": "m³/m³"
}

for column, unit in units.items():
    cursor.execute('''
        INSERT OR REPLACE INTO metadata (column_name, unit)
        VALUES (?, ?)
    ''', (column, unit))

conn.commit()
conn.close()
