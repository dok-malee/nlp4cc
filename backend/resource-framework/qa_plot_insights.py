import openai
from dotenv import load_dotenv
from openai import OpenAI
import os
import random
import time
import tkinter as tk
from tkinter import filedialog

random.seed(42)

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def get_gpt_result(system_role, question, max_tokens):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": question}
        ]
    )

    return completion


def save_python(ipt):
    py_file = open("plot_data_script.py", "w")
    py_file.write(ipt)
    py_file.close()


def execute_python_code():
    os.system("python plot_data_script.py")


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)  # use start += 1 to find overlapping matches


def extract_create_table(s):
    output = ''
    tables = s.split('CREATE TABLE')[1:]
    for table in tables:
        output += 'CREATE TABLE'
        output += table.split(');')[0]
        output += ');\n'

    return output


if __name__ == '__main__':
    file_path = "climate_data.db"
    print("Database file:", file_path)

    schema_path = "schema_weather_api.sql"
    print("Schema file:", schema_path)

    # ask user to ask a question
    question_original = input(
        "* Please enter your question (Press Enter to use the default question): \nWhat is the maximum temperature today? Draw a bar chart of last week's daily maximum temperature.")

    if question_original == '':
        question_original = ("What is the maximum temperature today? Draw a bar chart of last week's daily maximum temperature.")

    # get schema string
    schema_file = open(schema_path, 'r').read()

    schema = extract_create_table(schema_file)
    print("Extracted Schema file: ", schema)

    database = file_path

    # get GPT result
    system_role = '''Write python code to select relevant data and draw the chart and use the windows-1252 encoding. Please save the plot to "plot.pdf" and save the label and extracted values shown in the 
    plot to "plot_data.txt".'''

    question = "Question: " + question_original + '\n\nconn = sqlite3.connect("' + database + '")\n\nSchema: \n' + schema
    max_tokens = 2000

    print("*** Step1: generate code for extracting data and drawing the chart")
    print('* Question: ', question_original)
    input("* Press Enter to continue ...")

    start1 = time.time()
    print("* Calling GPT-3.5 API ...")
    response = get_gpt_result(system_role, question, max_tokens)
    text = response.choices[0].message.content

    # find python code
    try:
        matches = find_all(text, "```")
        matches_list = [x for x in matches]

        python = text[matches_list[0] + 10:matches_list[1]]

        # Remove 'python' from the first line if present
        python = '\n'.join(python.split('\n')[1:]) if python.startswith("python\n") else python
    except:
        python = text

    save_python(python)
    print("* Finished Step1")
    step1_time = int(time.time() - start1)
    print("* Time of Step1: ", step1_time, ' seconds\n')

    print("*** Step2: execute generated python script")

    input("* Press Enter to continue ...")
    start2 = time.time()
    execute_python_code()
    print("* Finished Step2")
    step2_time = int(time.time() - start2)
    print("* Time of Step2: ", step2_time, ' seconds\n')

    data = open('plot_data.txt', 'r').read()

    print("*** Step3: generate analysis and insights in 3 bullet points.")

    question = "Question: " + question_original + '\nData: \n' + data
    system_role = 'Generate analysis and insights about the data.'  # System role might need adjustment here

    start3 = time.time()
    print('* Start generating analysis and insights ...')

    response = get_gpt_result(system_role, question, max_tokens)

    text = response.choices[0].message.content

    print('* Response: \n', text)
    print("* Finished Step3")
    step3_time = int(time.time() - start3)
    print("* Time of Step3: ", step3_time, ' seconds\n')

    print('*** Total time: ', step1_time + step2_time + step3_time, ' seconds\n\n')

    response_file = open('analysis.txt', 'w')
    response_file.write(text)
    response_file.close()