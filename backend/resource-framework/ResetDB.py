import sqlite3

def reset_database():
    # Connect to SQLite database
    conn = sqlite3.connect('climate_data.db')
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS weather_data')
    cursor.execute('DROP TABLE IF EXISTS metadata')

    # Create the weather_data table with the defined schema
    cursor.execute('''
        CREATE TABLE weather_data (
            id INTEGER PRIMARY KEY,
            date TEXT UNIQUE,
            latitude TEXT,
            longitude TEXT,
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
            ragweed_pollen REAL,
            river_discharge REAL
        )
    ''')

    # Create the metadata table for units
    cursor.execute('''
        CREATE TABLE metadata (
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
        "soil_moisture_9_to_27cm": "m³/m³"
    }

    for column, unit in units.items():
        cursor.execute('''
            INSERT OR REPLACE INTO metadata (column_name, unit)
            VALUES (?, ?)
        ''', (column, unit))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset_database()
    print("Database has been reset.")

#%%
