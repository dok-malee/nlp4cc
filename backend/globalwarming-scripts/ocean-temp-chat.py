import os

import openai
import requests
from dotenv import load_dotenv
import pandas as pd
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# API endpoint URL
api_url = "https://global-warming.org/api/ocean-warming-api"
openai.api_key = os.getenv("OPENAI_API_KEY")



def fetch_ocean_warming_data(api_url):
    try:
        # Make a GET request to the API endpoint
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse JSON response
        data = response.json()

        # Extract relevant data from JSON
        if 'result' in data and isinstance(data['result'], dict):
            result_data = data['result']
        else:
            print("No result data found in the API response.")
            return None

        # Convert to Pandas DataFrame for easier manipulation
        df = pd.DataFrame(list(result_data.items()), columns=['Year', 'Temperature Anomaly (°C)'])

        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None


def format_output_for_chat(df):
    if df is None:
        return None

    formatted_output = ""

    # Format data into a readable string
    for index, row in df.iterrows():
        formatted_output += f"- Year {row['Year']}: Temperature Anomaly {row['Temperature Anomaly (°C)']}°C\n"

    return formatted_output.strip()

def get_gpt_insights(system_role, question, data):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=1500,
        temperature=0,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": f"{question}\n\nData:\n{data}"}
        ]
    )
    return response.choices[0].message


if __name__ == "__main__":
    # Fetch data from API
    ocean_data = fetch_ocean_warming_data(api_url)

    if ocean_data is not None:
        # Format the data for chat
        formatted_output = format_output_for_chat(ocean_data)

        if formatted_output:
            print("Formatted Ocean Warming Data:")
            print(formatted_output)

            system_role = (
                "You are a climate data analysis assistant. Generate analysis and insights about the data in 5 "
                "bullet points.")
            question = "What are the recent ocean warming trends?"

            insights = get_gpt_insights(system_role, question, formatted_output)

            print("Generated Insights:")
            print(insights)




