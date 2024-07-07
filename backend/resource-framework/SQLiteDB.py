import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('climate_data.db')
cursor = conn.cursor()

# Create the weather_data table with the defined schema if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY,
        date TEXT UNIQUE,
        location_code TEXT,
        temperature_2m_max REAL,
        temperature_2m_min REAL,
        uv_index_max REAL,
        precipitation_sum REAL,
        rain_sum REAL,
        showers_sum REAL,
        snowfall_sum REAL,
        precipitation_probability_max REAL,
        soil_moisture_1_to_3cm REAL,
        soil_moisture_9_to_27cm REAL,
        pm10 REAL,
        pm2_5 REAL,
        carbon_monoxide REAL,
        nitrogen_dioxide REAL,
        sulphur_dioxide REAL,
        ozone REAL,
        aerosol_optical_depth REAL,
        dust REAL,
        ammonia REAL,
        alder_pollen REAL,
        birch_pollen REAL,
        grass_pollen REAL,
        mugwort_pollen REAL,
        olive_pollen REAL,
        ragweed_pollen REAL
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
    "location_code": "String",
    "temperature_2m_max": "°C",
    "temperature_2m_min": "°C",
    "uv_index_max": "index",
    "precipitation_sum": "mm",
    "rain_sum": "mm",
    "showers_sum": "mm",
    "snowfall_sum": "mm",
    "precipitation_probability_max": "%",
    "soil_moisture_1_to_3cm": "m³/m³",
    "soil_moisture_9_to_27cm": "m³/m³",
    "pm10": "µg/m³",
    "pm2_5": "µg/m³",
    "carbon_monoxide": "mg/m³",
    "nitrogen_dioxide": "µg/m³",
    "sulphur_dioxide": "µg/m³",
    "ozone": "µg/m³",
    "aerosol_optical_depth": "dimensionless",
    "dust": "µg/m³",
    "ammonia": "µg/m³",
    "alder_pollen": "grains/m³",
    "birch_pollen": "grains/m³",
    "grass_pollen": "grains/m³",
    "mugwort_pollen": "grains/m³",
    "olive_pollen": "grains/m³",
    "ragweed_pollen": "grains/m³"
}

for column, unit in units.items():
    cursor.execute('''
        INSERT OR REPLACE INTO metadata (column_name, unit)
        VALUES (?, ?)
    ''', (column, unit))

conn.commit()
conn.close()
