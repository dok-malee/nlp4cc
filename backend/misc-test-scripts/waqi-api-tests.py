import os

import openai
import requests
from dotenv import load_dotenv
import json

def get_air_quality_data(station, token):
    url = f"http://api.waqi.info/feed/{station}/?token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch data (status code: {response.status_code})")
        return None


def main():
    # Retrieve the token from the environment variable
    load_dotenv()
    token = os.getenv('WAQI_TOKEN')

    if not token:
        print("Error: WAQI_TOKEN environment variable not set.")
        return

    station = 'bangkok'
    data = get_air_quality_data(station, token)
    if data:
        print(json.dumps(data, indent=4))


if __name__ == "__main__":
    main()
