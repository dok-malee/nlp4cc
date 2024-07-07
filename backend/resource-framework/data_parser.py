import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import sqlite3

# Set pandas display options to show more rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Define common API parameters
latitude = 48.13
longitude = 11.57
past_days = 7
forecast_days = 1

# Pull air quality data
url = "https://air-quality-api.open-meteo.com/v1/air-quality"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "aerosol_optical_depth", "dust", "ammonia", "alder_pollen", "birch_pollen", "grass_pollen", "mugwort_pollen", "olive_pollen", "ragweed_pollen"],
    "past_days": past_days,
    "forecast_days": forecast_days
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
hourly_pm2_5 = hourly.Variables(1).ValuesAsNumpy()
hourly_carbon_monoxide = hourly.Variables(2).ValuesAsNumpy()
hourly_nitrogen_dioxide = hourly.Variables(3).ValuesAsNumpy()
hourly_sulphur_dioxide = hourly.Variables(4).ValuesAsNumpy()
hourly_ozone = hourly.Variables(5).ValuesAsNumpy()
hourly_aerosol_optical_depth = hourly.Variables(6).ValuesAsNumpy()
hourly_dust = hourly.Variables(7).ValuesAsNumpy()
hourly_ammonia = hourly.Variables(8).ValuesAsNumpy()
hourly_alder_pollen = hourly.Variables(9).ValuesAsNumpy()
hourly_birch_pollen = hourly.Variables(10).ValuesAsNumpy()
hourly_grass_pollen = hourly.Variables(11).ValuesAsNumpy()
hourly_mugwort_pollen = hourly.Variables(12).ValuesAsNumpy()
hourly_olive_pollen = hourly.Variables(13).ValuesAsNumpy()
hourly_ragweed_pollen = hourly.Variables(14).ValuesAsNumpy()

hourly_data_air_quality = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "pm10": hourly_pm10,
    "pm2_5": hourly_pm2_5,
    "carbon_monoxide": hourly_carbon_monoxide,
    "nitrogen_dioxide": hourly_nitrogen_dioxide,
    "sulphur_dioxide": hourly_sulphur_dioxide,
    "ozone": hourly_ozone,
    "aerosol_optical_depth": hourly_aerosol_optical_depth,
    "dust": hourly_dust,
    "ammonia": hourly_ammonia,
    "alder_pollen": hourly_alder_pollen,
    "birch_pollen": hourly_birch_pollen,
    "grass_pollen": hourly_grass_pollen,
    "mugwort_pollen": hourly_mugwort_pollen,
    "olive_pollen": hourly_olive_pollen,
    "ragweed_pollen": hourly_ragweed_pollen
}
hourly_dataframe_air_quality = pd.DataFrame(data=hourly_data_air_quality)

# Compute daily averages for air quality values
hourly_dataframe_air_quality['date'] = hourly_dataframe_air_quality['date'].dt.date  # Convert to date only
daily_averages_air_quality = hourly_dataframe_air_quality.groupby('date').mean().reset_index()

# Pull weather data
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": ["soil_moisture_1_to_3cm", "soil_moisture_9_to_27cm"],
    "daily": ["temperature_2m_max", "temperature_2m_min", "uv_index_max", "precipitation_sum", "rain_sum",
              "showers_sum", "snowfall_sum", "precipitation_probability_max"],
    "timezone": "auto",
    "past_days": past_days,
    "forecast_days": forecast_days
}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# Generate a location code based on latitude and longitude
location_code = f"{latitude}_{longitude}"

# Process hourly weather data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_soil_moisture_1_to_3cm = hourly.Variables(0).ValuesAsNumpy()
hourly_soil_moisture_9_to_27cm = hourly.Variables(1).ValuesAsNumpy()

hourly_data_weather = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "soil_moisture_1_to_3cm": hourly_soil_moisture_1_to_3cm,
    "soil_moisture_9_to_27cm": hourly_soil_moisture_9_to_27cm
}
hourly_dataframe_weather = pd.DataFrame(data=hourly_data_weather)

# Compute daily averages for soil moisture values
hourly_dataframe_weather['date'] = hourly_dataframe_weather['date'].dt.date  # Convert to date only
daily_averages_weather = hourly_dataframe_weather.groupby('date').mean().reset_index()

# Process daily weather data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_data_weather = {
    "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(days=1),
        inclusive="left"
    ),
    "temperature_2m_max": daily.Variables(0).ValuesAsNumpy(),
    "temperature_2m_min": daily.Variables(1).ValuesAsNumpy(),
    "uv_index_max": daily.Variables(2).ValuesAsNumpy(),
    "precipitation_sum": daily.Variables(3).ValuesAsNumpy(),
    "rain_sum": daily.Variables(4).ValuesAsNumpy(),
    "showers_sum": daily.Variables(5).ValuesAsNumpy(),
    "snowfall_sum": daily.Variables(6).ValuesAsNumpy(),
    "precipitation_probability_max": daily.Variables(7).ValuesAsNumpy()
}
daily_dataframe_weather = pd.DataFrame(data=daily_data_weather)

# Ensure date columns are in the same format
daily_dataframe_weather['date'] = pd.to_datetime(daily_dataframe_weather['date']).dt.date

# Merge daily averages with daily data
final_daily_dataframe_weather = pd.merge(daily_dataframe_weather, daily_averages_weather, on='date', suffixes=('', '_avg'))

# Add location_code to the DataFrame
final_daily_dataframe_weather['location_code'] = location_code

# Merge air quality data
final_daily_dataframe = pd.merge(final_daily_dataframe_weather, daily_averages_air_quality, on='date', how='left')

# Connect to SQLite database and insert or update data
conn = sqlite3.connect('climate_data.db')
cursor = conn.cursor()

# Create the table if it does not exist and update the schema to accommodate all data fields
cursor.execute('''
CREATE TABLE IF NOT EXISTS weather_data (
    date TEXT PRIMARY KEY,
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

# Insert or update data into the weather_data table
for _, row in final_daily_dataframe.iterrows():
    # Extract values and round them before insertion
    data = (
        row['date'],
        row['location_code'],
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
        round(row['ragweed_pollen'], 2)
    )
    # Print the rounded data to verify
    print(f"Inserting row: {data}")
    cursor.execute('''
        INSERT INTO weather_data (date, location_code, temperature_2m_max, temperature_2m_min, uv_index_max, precipitation_sum, rain_sum, 
        showers_sum, snowfall_sum, precipitation_probability_max, soil_moisture_1_to_3cm, soil_moisture_9_to_27cm,
        pm10, pm2_5, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, ozone, aerosol_optical_depth, dust, ammonia, alder_pollen, birch_pollen,
        grass_pollen, mugwort_pollen, olive_pollen, ragweed_pollen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            location_code = excluded.location_code,
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
            ragweed_pollen = excluded.ragweed_pollen
    ''', data)

conn.commit()
conn.close()
