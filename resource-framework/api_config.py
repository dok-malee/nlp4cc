# config.py

latitude = 48.13
longitude = 11.57
past_days = 7
forecast_days = 1

url_flood = "https://flood-api.open-meteo.com/v1/flood"
params_flood = {
    "latitude": latitude,
    "longitude": longitude,
    "daily": "river_discharge",
    "past_days": past_days,
    "forecast_days": forecast_days
}

url_aq = "https://air-quality-api.open-meteo.com/v1/air-quality"
params_aq = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "aerosol_optical_depth", "dust", "ammonia", "alder_pollen", "birch_pollen", "grass_pollen", "mugwort_pollen", "olive_pollen", "ragweed_pollen"],
    "past_days": past_days,
    "forecast_days": forecast_days
}

url_weather = "https://api.open-meteo.com/v1/forecast"
params_weather = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": ["soil_moisture_1_to_3cm", "soil_moisture_9_to_27cm"],
    "daily": ["temperature_2m_max", "temperature_2m_min", "uv_index_max", "precipitation_sum", "rain_sum",
              "showers_sum", "snowfall_sum", "precipitation_probability_max"],
    "timezone": "auto",
    "past_days": past_days,
    "forecast_days": forecast_days
}
