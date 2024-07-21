import openai
from dotenv import load_dotenv
from openai import OpenAI
import os
import random
import time

# Change here
qa_id = 10
question = (
    'Analyze the frequency and intensity of droughts from 2024 compared to historical data from 1980-2023. Discuss '
    'the potential implications for water resources and local ecosystems.')
# model = "gpt-3.5-turbo"
model = "gpt-4o"

second_system_prompt_gpt35 = (
    "Write an extensive report based on the provided data for Munich. "
    "If historic data is provided and relevant to the question, include a trend analysis to highlight changes and "
    "trends over time in the context of climate change. "
    "Finally, provide a detailed answer to the user question if a question is presented."
)

second_system_prompt_gpt4o = (
    "Write an extensive report based on the provided data for Munich. "
    # Necessary for GPT-4o to use DB data, otherwise will just query internet
    "Try to focus on the data provided in the databases first, before querying from the internet. "
    "If historic data is provided and relevant to the question, include a trend analysis to highlight changes and "
    "trends over time in the context of climate change. "
    "Finally, provide a detailed answer to the user question if a question is presented."
)

random.seed(42)

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def get_gpt_result(system_role, question, max_tokens):
    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": question}
        ]
    )

    return completion


def save_python(ipt):
    py_file = open(f"{qa_id}_script.py", "w")
    py_file.write(ipt)
    py_file.close()


def execute_python_code():
    os.system(f"python {qa_id}_script.py")


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

    schema_path = "climate_schema.sql"
    print("Schema file:", schema_path)

    hist_schema_path = "historic_climate_schema.sql"
    print("Schema file:", hist_schema_path)

    question_original = question

    # get schema string
    schema_file = open(schema_path, 'r').read()
    schema = extract_create_table(schema_file)

    hist_schema_file = open(hist_schema_path, 'r').read()
    hist_schema = extract_create_table(hist_schema_file)

    print("Extracted Schema files: ", schema + "\n" + hist_schema)

    database = file_path

    # get GPT result
    system_role = f'''Write python code to select and save relevant data from the database. Please save the retrieved 
    values from the database to "{qa_id}_data.txt".
    Note: Historic Data is only provided from 1980 to 2023 for the days 07-01 to 07-09. '''

    question = (
    "Question/Prompt: " + question_original + '\n\n'
    "conn = sqlite3.connect('" + database + "')\n\n"
    "Current Weather Schema for the year 2024:\n" + schema + '\n\n'
    "Historic Weather Schema from 1980 to 2023:\n" + hist_schema + '\n\n'
    )

    max_tokens = 2000

    print("*** Step1: generate code for extracting data")
    print('* Question/Prompt: ', question_original)
    input("* Press Enter to continue ...")

    start1 = time.time()
    print(f"* Calling {model} API ...")
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

    if not os.path.exists(f'{qa_id}_data.txt'):
        with open(f'{qa_id}_data.txt', 'w') as response_file:
            pass

    data = open(f'{qa_id}_data.txt', 'r').read()

    print("*** Step3: generate report")

    question = "Question: " + question_original + '\nData: \n' + data

    if model == 'gpt-4o':
        second_system_prompt = second_system_prompt_gpt4o
    else:
        second_system_prompt = second_system_prompt_gpt35

    start3 = time.time()
    print('* Start generating report ...')

    response = get_gpt_result(second_system_prompt, question, max_tokens)

    text = response.choices[0].message.content

    print('* Response: \n', text)
    print("* Finished Step3")
    step3_time = int(time.time() - start3)
    print("* Time of Step3: ", step3_time, ' seconds\n')

    print('*** Total time: ', step1_time + step2_time + step3_time, ' seconds\n\n')

    if not os.path.exists(f'{qa_id}_analysis.txt'):
        with open(f'{qa_id}_analysis.txt', 'w') as response_file:
            pass

    response_file = open(f'{qa_id}_analysis.txt', 'w')
    response_file.write(text)
    response_file.close()
