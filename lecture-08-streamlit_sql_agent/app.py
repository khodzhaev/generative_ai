import streamlit as st
import sqlite3
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Агент формирует SQL-запрос, получает ответ и превращает его в человеческий язык
def ask_agent(question):
    messages = [{"role": "user", "content": question}]
    functions = [{
        "name": "query_database",
        "description": "Query the orders database using SQLite SQL. Use SQLite date functions like strftime('%Y-%m', date) for date operations. The orders table has columns: id, order_date, customer_name, amount.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQLite query to run on the orders database. Use strftime() for date operations."
                }
            },
            "required": ["query"]
        }
    }]

    # 1. Получаем SQL-запрос
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        functions=functions,
        function_call="auto"
    )

    choice = response.choices[0]

    if choice.finish_reason == "function_call":
        query = json.loads(choice.message.function_call.arguments)["query"]
        result = run_query(query)

        # 2. Формируем финальный ответ — снова спрашиваем у GPT, как красиво это сказать
        final_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты помощник, который объясняет результат SQL-запросов человеку простым языком как финансист."},
                {"role": "user", "content": f"Вопрос: {question}"},
                {"role": "assistant", "content": f"SQL-запрос: {query}"},
                {"role": "assistant", "content": f"Результат: {result}"}
            ]
        )
        return final_response.choices[0].message.content
    else:
        return choice.message.content

# Выполнение SQL-запроса
def run_query(query):
    conn = sqlite3.connect("../business_data.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        return [[str(e)]]
    finally:
        conn.close()

# Streamlit UI
st.title("🧠 SQL Agent over Orders DB")
question = st.text_input("Задай вопрос агенту (например: Сколько заказов было в январе 2023?)")

if st.button("Спросить"):
    if not question:
        st.warning("Введите вопрос!")
    else:
        response = ask_agent(question)
        st.markdown(f"📊 **Ответ:** {response}")
