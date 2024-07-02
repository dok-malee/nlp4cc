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

# Define API parameters
latitude = 48.13
longitude = 11.57

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": ["soil_moisture_1_to_3cm", "soil_moisture_9_to_27cm"],
    "daily": ["temperature_2m_max", "temperature_2m_min", "uv_index_max", "precipitation_sum", "rain_sum",
              "showers_sum", "snowfall_sum", "precipitation_probability_max"],
    "timezone": "auto",
    "past_days": 7,  # 1 for test purposes, change to 7 later
    "forecast_days": 1
}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# Generate a location code based on latitude and longitude
location_code = f"{latitude}_{longitude}"

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_soil_moisture_1_to_3cm = hourly.Variables(0).ValuesAsNumpy()
hourly_soil_moisture_9_to_27cm = hourly.Variables(1).ValuesAsNumpy()

hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "soil_moisture_1_to_3cm": hourly_soil_moisture_1_to_3cm,
    "soil_moisture_9_to_27cm": hourly_soil_moisture_9_to_27cm
}
hourly_dataframe = pd.DataFrame(data=hourly_data)

# Compute daily averages for soil moisture values
hourly_dataframe['date'] = hourly_dataframe['date'].dt.date  # Convert to date only
daily_averages = hourly_dataframe.groupby('date').mean().reset_index()

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_data = {
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
daily_dataframe = pd.DataFrame(data=daily_data)

# Ensure date columns are in the same format
daily_dataframe['date'] = pd.to_datetime(daily_dataframe['date']).dt.date

# Merge daily averages with daily data
final_daily_dataframe = pd.merge(daily_dataframe, daily_averages, on='date', suffixes=('', '_avg'))

# Add location_code to the DataFrame
final_daily_dataframe['location_code'] = location_code

print(final_daily_dataframe)

# Connect to SQLite database and insert or update data
conn = sqlite3.connect('climate_data.db')
cursor = conn.cursor()

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
        round(row['soil_moisture_9_to_27cm'], 2)
    )
    # Print the rounded data to verify
    print(f"Inserting row: {data}")
    cursor.execute('''
        INSERT INTO weather_data (date, location_code, temperature_2m_max, temperature_2m_min, uv_index_max, precipitation_sum, rain_sum, 
        showers_sum, snowfall_sum, precipitation_probability_max, soil_moisture_1_to_3cm, soil_moisture_9_to_27cm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            soil_moisture_9_to_27cm = excluded.soil_moisture_9_to_27cm
    ''', data)

conn.commit()
conn.close()

#%%
