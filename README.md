# Creating (Weather) Reports using Real-Time Data and LLMs

## Description
This project explores how climate-related APIs can be used in combination with Large Language Models (LLMs) to enhance the context and discussion around climate change. By integrating real-time data, we aim to provide a more accessible perspective on climate data.
We saved data from the API for this year from 2024-05-14 to 2024-07-16. Historic Data is only provided from 1980 to 2023 for the days 07-01 to 07-09.

## APIs Used
- https://open-meteo.com/ (Weather, AQI, Flood, Historical Data)

Other possibly useful API's can be seen under Climate-APIs.md

## Database
- SQLite

## LLM
- GPT-3.5-turbo
- GPT-4o
- ClimateGPT

## Results
- [Results Excel](https://docs.google.com/spreadsheets/d/1-3PJ9CU_dea3ZjGgZRRrBxNqmNQ2pxBdcKT6NUP86bg/edit?usp=sharing)


## How to Use
1. Get OpenAI API Key and set in .env (view .env.example)
2. Install requirements
3. Run qa_insights.py with set question and model
