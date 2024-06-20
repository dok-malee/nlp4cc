import os

import openai
from dotenv import load_dotenv
from openai import OpenAI

# Replace 'your-api-key' with your actual OpenAI API key
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)

print(completion.choices[0].message)
