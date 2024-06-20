import os
import openai
import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

co2_api_url = 'https://global-warming.org/api/co2-api'
ocean_api_url = "https://global-warming.org/api/ocean-warming-api"


# Function to fetch CO2 data from the API
def fetch_co2_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None


# Function to calculate average CO2 levels per year
def calculate_avg_co2_levels(co2_data):
    if co2_data:
        co2_data = co2_data['co2']

        # Convert data to DataFrame
        df = pd.DataFrame(co2_data)

        # Convert numeric columns to float for calculation (if necessary)
        df['cycle'] = pd.to_numeric(df['cycle'])
        df['trend'] = pd.to_numeric(df['trend'])

        # Convert year column to numeric
        df['year'] = pd.to_numeric(df['year'])

        # Calculate average CO2 levels per year
        avg_co2_per_year = df.groupby('year').agg({'cycle': 'mean', 'trend': 'mean'}).reset_index()

        return avg_co2_per_year
    else:
        return None


# Function to fetch ocean temperature data from the API
def fetch_ocean_warming_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()

        if 'result' in data and isinstance(data['result'], dict):
            result_data = data['result']
        else:
            print("No result data found in the API response.")
            return None

        df = pd.DataFrame(list(result_data.items()), columns=['Year', 'Temperature Anomaly (°C)'])
        df['Year'] = pd.to_numeric(df['Year'])
        df['Temperature Anomaly (°C)'] = pd.to_numeric(df['Temperature Anomaly (°C)'])

        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None


# Function to format the combined output for chat
def format_combined_output_for_chat(co2_df, ocean_df):
    combined_df = pd.merge(co2_df, ocean_df, left_on='year', right_on='Year', how='inner')

    formatted_output = ""
    for _, row in combined_df.iterrows():
        formatted_output += (
            f"Year: {row['year']}, "
            f"Avg CO2 Cycle: {row['cycle']:.2f}, "
            f"Avg CO2 Trend: {row['trend']:.2f}, "
            f"Ocean Temperature Anomaly: {row['Temperature Anomaly (°C)']:.2f}°C\n"
        )
    return formatted_output.strip()


# Function to get insights using OpenAI GPT
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
    # Fetch CO2 data from the API
    co2_data = fetch_co2_data(co2_api_url)

    if co2_data is not None:
        # Calculate average CO2 levels per year
        avg_co2_per_year = calculate_avg_co2_levels(co2_data)

        # Fetch ocean temperature data from the API
        ocean_data = fetch_ocean_warming_data(ocean_api_url)

        if avg_co2_per_year is not None and ocean_data is not None:
            # Format the combined output for chat
            formatted_output = format_combined_output_for_chat(avg_co2_per_year, ocean_data)

            if formatted_output:
                print("Formatted Combined Data:")
                print(formatted_output)

                # Prepare inputs for OpenAI GPT
                system_role = (
                    "You are a climate data analysis assistant. Generate analysis and insights about the data "
                    "according to the users question."
                )
                question = ("Why are the ocean temperatures increasing and what are ")

                # Get insights from OpenAI GPT
                insights = get_gpt_insights(system_role, question, formatted_output)

                print("Generated Insights:")
                print(insights)
        else:
            print("Failed to calculate average CO2 levels per year or fetch ocean temperature data.")
    else:
        print("Failed to fetch CO2 data from the API.")
