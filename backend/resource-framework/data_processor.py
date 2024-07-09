import pandas as pd
from api_config import latitude, longitude


def process_flood_data(response_flood):
    daily = response_flood.Daily()
    daily_river_discharge = daily.Variables(0).ValuesAsNumpy()
    daily_data_flood = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "river_discharge": daily_river_discharge
    }
    daily_dataframe_flood = pd.DataFrame(data=daily_data_flood)
    daily_dataframe_flood['date'] = pd.to_datetime(daily_dataframe_flood['date']).dt.date
    return daily_dataframe_flood


def process_air_quality_data(response_aq):
    hourly = response_aq.Hourly()
    hourly_data_air_quality = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "pm10": hourly.Variables(0).ValuesAsNumpy(),
        "pm2_5": hourly.Variables(1).ValuesAsNumpy(),
        "carbon_monoxide": hourly.Variables(2).ValuesAsNumpy(),
        "nitrogen_dioxide": hourly.Variables(3).ValuesAsNumpy(),
        "sulphur_dioxide": hourly.Variables(4).ValuesAsNumpy(),
        "ozone": hourly.Variables(5).ValuesAsNumpy(),
        "aerosol_optical_depth": hourly.Variables(6).ValuesAsNumpy(),
        "dust": hourly.Variables(7).ValuesAsNumpy(),
        "ammonia": hourly.Variables(8).ValuesAsNumpy(),
        "alder_pollen": hourly.Variables(9).ValuesAsNumpy(),
        "birch_pollen": hourly.Variables(10).ValuesAsNumpy(),
        "grass_pollen": hourly.Variables(11).ValuesAsNumpy(),
        "mugwort_pollen": hourly.Variables(12).ValuesAsNumpy(),
        "olive_pollen": hourly.Variables(13).ValuesAsNumpy(),
        "ragweed_pollen": hourly.Variables(14).ValuesAsNumpy()
    }
    hourly_dataframe_air_quality = pd.DataFrame(data=hourly_data_air_quality)
    hourly_dataframe_air_quality['date'] = hourly_dataframe_air_quality['date'].dt.date
    daily_averages_air_quality = hourly_dataframe_air_quality.groupby('date').mean().reset_index()
    return daily_averages_air_quality


def process_weather_data(response_weather):
    hourly = response_weather.Hourly()
    hourly_data_weather = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "soil_moisture_1_to_3cm": hourly.Variables(0).ValuesAsNumpy(),
        "soil_moisture_9_to_27cm": hourly.Variables(1).ValuesAsNumpy()
    }
    hourly_dataframe_weather = pd.DataFrame(data=hourly_data_weather)
    hourly_dataframe_weather['date'] = hourly_dataframe_weather['date'].dt.date
    daily_averages_weather = hourly_dataframe_weather.groupby('date').mean().reset_index()

    daily = response_weather.Daily()
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
    daily_dataframe_weather['date'] = pd.to_datetime(daily_dataframe_weather['date']).dt.date

    final_daily_dataframe_weather = pd.merge(daily_dataframe_weather, daily_averages_weather, on='date',
                                             suffixes=('', '_avg'))
    return final_daily_dataframe_weather


def merge_data(weather_df, air_quality_df, flood_df):
    weather_df['latitude'] = latitude
    weather_df['longitude'] = longitude
    final_daily_dataframe = pd.merge(weather_df, air_quality_df, on='date', how='left')
    final_daily_dataframe = pd.merge(final_daily_dataframe, flood_df, on='date', how='left')
    final_daily_dataframe.fillna(0, inplace=True)
    return final_daily_dataframe
