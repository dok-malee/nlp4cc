import os

import openai
import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

api_url = 'https://global-warming.org/api/co2-api'

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

        # Format the output as a list of dictionaries
        avg_co2_per_year_list = avg_co2_per_year.to_dict(orient='records')

        return avg_co2_per_year_list
    else:
        return None

# Function to format the output for chat
def format_output_for_chat(avg_co2_per_year_list):
    if avg_co2_per_year_list:
        formatted_output = ""
        for record in avg_co2_per_year_list:
            formatted_output += f"Year: {record['year']}, Avg Cycle: {record['cycle']:.2f}, Avg Trend: {record['trend']:.2f}\n"
        return formatted_output.strip()
    else:
        return None

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
    co2_data = fetch_co2_data(api_url)

    if co2_data is not None:
        # Calculate average CO2 levels per year
        avg_co2_per_year_list = calculate_avg_co2_levels(co2_data)

        if avg_co2_per_year_list:
            # Format the output for chat
            formatted_output = format_output_for_chat(avg_co2_per_year_list)

            if formatted_output:
                print("Formatted Data:")
                print(formatted_output)

                # Prepare inputs for OpenAI GPT
                system_role = (
                    "You are a climate data analysis assistant. Generate analysis and insights about the data in 3 "
                    "bullet points.")
                question = "What are the trends in CO2 levels over the years"

                # Get insights from OpenAI GPT
                insights = get_gpt_insights(system_role, question, formatted_output)

                print("Generated Insights:")
                print(insights)
        else:
            print("Failed to calculate average CO2 levels per year.")
    else:
        print("Failed to fetch CO2 data from the API.")
