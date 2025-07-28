
import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def query_database(sql_query):
    conn = sqlite3.connect("../business_data.db")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    result = cursor.fetchall()
    conn.close()
    return result

functions = [
    {
        "name": "query_database",
        "description": "Run an SQL query on the orders database",
        "parameters": {
            "type": "object",
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "The SQL query to run on the orders table",
                },
            },
            "required": ["sql_query"],
        },
    }
]

user_question = input("Enter your question about orders: ")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that knows how to write SQL queries for a SQLite database with a table 'orders' (id, customer_name, order_date, amount)."},
        {"role": "user", "content": user_question}
    ],
    functions=functions,
    function_call="auto",
)

function_call = response.choices[0].message.function_call
arguments = json.loads(function_call.arguments)
sql_query = arguments["sql_query"]

sql_result = query_database(sql_query)

response_final = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_question},
        {"role": "function", "name": function_call.name, "content": str(sql_result)},
    ]
)

print("Ответ:", response_final.choices[0].message.content)
