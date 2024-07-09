import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import sqlite3
from api_config import latitude, longitude, url_flood, params_flood, url_aq, params_aq, url_weather, params_weather
from data_fetcher import fetch_flood_data, fetch_air_quality_data, fetch_weather_data
from data_processor import process_flood_data, process_air_quality_data, process_weather_data, merge_data

# Set pandas display options to show more rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

# Set up the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Fetch data
response_flood = fetch_flood_data(openmeteo)
response_aq = fetch_air_quality_data(openmeteo)
response_weather = fetch_weather_data(openmeteo)

# Process data
daily_dataframe_flood = process_flood_data(response_flood)
daily_averages_air_quality = process_air_quality_data(response_aq)
final_daily_dataframe_weather = process_weather_data(response_weather)

# Merge data
final_daily_dataframe = merge_data(final_daily_dataframe_weather, daily_averages_air_quality, daily_dataframe_flood)
print(final_daily_dataframe)

# Connect to SQLite database and insert or update data
conn = sqlite3.connect('climate_data.db')
cursor = conn.cursor()

# Create the table if it does not exist and update the schema to accommodate all data fields
cursor.execute('''
CREATE TABLE IF NOT EXISTS weather_data (
    date TEXT PRIMARY KEY,
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

# Insert or update data into the weather_data table
for _, row in final_daily_dataframe.iterrows():
    # Extract values and round them before insertion
    data = (
        row['date'],
        row['latitude'],
        row['longitude'],
        round(row['temperature_2m_max'], 2),
        round(row['temperature_2m_min'], 2),
        round(row['uv_index_max'], 2),
        round(row['precipitation_sum'], 2),
        round(row['rain_sum'], 2),
        round(row['showers_sum'], 2),
        round(row['snowfall_sum'], 2),
        round(row['precipitation_probability_max'], 2),
        round(row['soil_moisture_1_to_3cm'], 2),
        round(row['soil_moisture_9_to_27cm'], 2),
        round(row['pm10'], 2),
        round(row['pm2_5'], 2),
        round(row['carbon_monoxide'], 2),
        round(row['nitrogen_dioxide'], 2),
        round(row['sulphur_dioxide'], 2),
        round(row['ozone'], 2),
        round(row['aerosol_optical_depth'], 2),
        round(row['dust'], 2),
        round(row['ammonia'], 2),
        round(row['alder_pollen'], 2),
        round(row['birch_pollen'], 2),
        round(row['grass_pollen'], 2),
        round(row['mugwort_pollen'], 2),
        round(row['olive_pollen'], 2),
        round(row['ragweed_pollen'], 2),
        round(row['river_discharge'], 2)
    )
    print(f"Inserting row: {data}")

    cursor.execute('''
        INSERT INTO weather_data (date, latitude, longitude, temperature_2m_max, temperature_2m_min, uv_index_max, precipitation_sum, rain_sum,
        showers_sum, snowfall_sum, precipitation_probability_max, soil_moisture_1_to_3cm, soil_moisture_9_to_27cm,
        pm10, pm2_5, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, ozone, aerosol_optical_depth, dust, ammonia, alder_pollen, birch_pollen,
        grass_pollen, mugwort_pollen, olive_pollen, ragweed_pollen, river_discharge)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            temperature_2m_max = excluded.temperature_2m_max,
            temperature_2m_min = excluded.temperature_2m_min,
            uv_index_max = excluded.uv_index_max,
            precipitation_sum = excluded.precipitation_sum,
            rain_sum = excluded.rain_sum,
            showers_sum = excluded.showers_sum,
            snowfall_sum = excluded.snowfall_sum,
            precipitation_probability_max = excluded.precipitation_probability_max,
            soil_moisture_1_to_3cm = excluded.soil_moisture_1_to_3cm,
            soil_moisture_9_to_27cm = excluded.soil_moisture_9_to_27cm,
            pm10 = excluded.pm10,
            pm2_5 = excluded.pm2_5,
            carbon_monoxide = excluded.carbon_monoxide,
            nitrogen_dioxide = excluded.nitrogen_dioxide,
            sulphur_dioxide = excluded.sulphur_dioxide,
            ozone = excluded.ozone,
            aerosol_optical_depth = excluded.aerosol_optical_depth,
            dust = excluded.dust,
            ammonia = excluded.ammonia,
            alder_pollen = excluded.alder_pollen,
            birch_pollen = excluded.birch_pollen,
            grass_pollen = excluded.grass_pollen,
            mugwort_pollen = excluded.mugwort_pollen,
            olive_pollen = excluded.olive_pollen,
            ragweed_pollen = excluded.ragweed_pollen,
            river_discharge = excluded.river_discharge
    ''', data)

conn.commit()
conn.close()
