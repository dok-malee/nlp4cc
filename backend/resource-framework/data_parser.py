import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
from geopy.geocoders import Nominatim

# Set pandas display options to show more rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "hourly": ["soil_moisture_1_to_3cm", "soil_moisture_9_to_27cm"],
    "daily": ["temperature_2m_max", "temperature_2m_min", "uv_index_max", "precipitation_sum", "rain_sum",
              "showers_sum", "snowfall_sum", "precipitation_probability_max"],
    "timezone": "auto",
    "past_days": 1,  # 1 for test purposes, change to 7 later
    "forecast_days": 1
}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# Get city name using geopy
geolocator = Nominatim(user_agent='your_app_name')
location = geolocator.reverse((response.Latitude(), response.Longitude()))
city_name = location.raw['address'].get('city', 'Unknown')

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
daily_averages['date'] = pd.to_datetime(daily_averages['date']).dt.date

# Merge daily averages with daily data
final_daily_dataframe = pd.merge(daily_dataframe, daily_averages, on='date')

# Add city name column (Maybe there is a better solution than adding the city repetitively in a new column?)
final_daily_dataframe['city'] = city_name

print(final_daily_dataframe)
