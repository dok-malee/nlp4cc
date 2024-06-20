import os
import requests_cache
import pandas as pd
from retry_requests import retry
from dotenv import load_dotenv
import openmeteo_requests

# Load environment variables
load_dotenv()

# Set up the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


def fetch_air_quality_data(latitude, longitude, forecast_days):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "european_aqi",
        "hourly": ["pm10", "pm2_5"],
        "forecast_days": forecast_days
    }
    response = openmeteo.weather_api(url, params=params)
    return response[0]


def process_response(response, forecast_days):
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Current values
    current = response.Current()
    current_european_aqi = current.Variables(0).Value()
    print(f"Current time {current.Time()}")
    print(f"Current european_aqi {current_european_aqi}")

    # Process hourly data
    hourly = response.Hourly()
    hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
    hourly_pm2_5 = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "pm10": hourly_pm10,
        "pm2_5": hourly_pm2_5
    }

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    print("\nHourly Data:")
    print(hourly_dataframe)

    # Calculate the daily averages for PM10 and PM2.5 if more than one forecast day is specified
    if forecast_days > 1:
        daily_avg = hourly_dataframe.resample('D', on='date').mean()
        print("\nDaily Averages:")
        print(daily_avg)
        return daily_avg
    else:
        return hourly_dataframe


def main(locations, forecast_days):
    for location in locations:
        latitude, longitude = location
        response = fetch_air_quality_data(latitude, longitude, forecast_days)
        processed_data = process_response(response, forecast_days)
        # Here you can further process the `processed_data` for GPT-3.5 API or other purposes
        print(processed_data)


if __name__ == "__main__":
    # Define locations (latitude, longitude) and forecast days
    locations = [(52.52, 13.41), (13.7563, 100.5018)]
    forecast_days = 1  # Change this value to fetch multiple days if needed

    # Run the main function
    main(locations, forecast_days)
