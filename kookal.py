import pathlib
import textwrap
import mysql.connector
import google.generativeai as genai

import pandas as pd

from IPython.display import display
from IPython.display import Markdown

import mysql.connector
import streamlit as st
import random
import time
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="SurSql2007!"
)
mycursor = mydb.cursor()
mycursor.execute("USE sys")
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

genai.configure(api_key="AIzaSyBVGSAlqn7Q5gKHNU_ntBhy-PGFYt-o7as")
model = genai.GenerativeModel('gemini-1.5-flash')
query = """Given the following SQL tables, your job is to only queries without any explanation given a user’s request.
regions: Stores regions with a unique region_id as primary key and region_name.

countries:
Contains countries information with country_id as the primary key, country_name, and region_id linking to the regions table.

locations:
Stores specific location details such as location_id, street_address, postal_code, city, state_province, and country_id linking to the countries table.

jobs:
Records different job positions with job_id as primary key, job_title, min_salary, and max_salary.

departments:
Holds department information with department_id as primary key, department_name, and location_id linking to the locations table.

employees:
Stores employee data including employee_id as primary key, first_name, last_name, email, phone_number, hire_date, job_id, salary, manager_id, and department_id linking to respective tables (jobs, departments, employees for manager).

dependents:
Contains details of dependents of employees with dependent_id as primary key, first_name, last_name, relationship, and employee_id linking to the employees table."""


# Streamed response emulator
def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.1)


st.title("Simple chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Enter query"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)


    query = query + prompt
    response = model.generate_content(query)
    code=response.text
    code = code[code.find('\n')+1:code.rfind('\n')]

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(code))
        mycursor.execute(code)
        myresult = mycursor.fetchall()

        for x in myresult:
            print(x)
        message = {"role": "assistant", "content": response}
        data = pd.DataFrame.from_dict(myresult)
        st.dataframe(data)
        data_html = data.to_html(index=False, justify='center')
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})