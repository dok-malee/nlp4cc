from api_config import url_flood, params_flood, url_aq, params_aq, url_weather, params_weather
import openmeteo_requests


def fetch_flood_data(openmeteo):
    responses_flood = openmeteo.weather_api(url_flood, params=params_flood)
    return responses_flood[0]


def fetch_air_quality_data(openmeteo):
    responses_aq = openmeteo.weather_api(url_aq, params=params_aq)
    return responses_aq[0]


def fetch_weather_data(openmeteo):
    responses_weather = openmeteo.weather_api(url_weather, params=params_weather)
    return responses_weather[0]
