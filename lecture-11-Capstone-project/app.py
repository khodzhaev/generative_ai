import streamlit as st
import sqlite3
import pandas as pd
from openai import OpenAI
import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DB_PATH = "../business_data.db"
LOG_FILE = "query_log.txt"

def run_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)

def log_console(message):
    print(f"[LOG] {datetime.now().isoformat()} - {message}")

def log_to_file(question, answer):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] QUESTION:\n{question}\nANSWER:\n{answer}\n\n")

def normalize_sql(query):
    q = query
    q = (
        q.replace("transactions", "orders")
         .replace("order_order_date", "order_date")
    )
    q = re.sub(r"\bdate\b", "order_date", q, flags=re.IGNORECASE)
    q = re.sub(r"DATE_PART\(\s*'year'\s*,\s*([^)]+)\)", r"strftime('%Y', \1)", q, flags=re.IGNORECASE)
    q = re.sub(r"DATE_PART\(\s*'month'\s*,\s*([^)]+)\)", r"strftime('%m', \1)", q, flags=re.IGNORECASE)
    q = re.sub(r"EXTRACT\s*\(\s*YEAR\s+FROM\s+([^)]+)\)", r"strftime('%Y', \1)", q, flags=re.IGNORECASE)
    q = re.sub(r"EXTRACT\s*\(\s*MONTH\s+FROM\s+([^)]+)\)", r"strftime('%m', \1)", q, flags=re.IGNORECASE)
    q = re.sub(r"YEAR\s*\(\s*([^)]+)\)", r"strftime('%Y', \1)", q, flags=re.IGNORECASE)
    q = re.sub(r"MONTH\s*\(\s*([^)]+)\)", r"strftime('%m', \1)", q, flags=re.IGNORECASE)
    q = re.sub(r"(strftime\('%Y',\s*[^)]+\)\s*=\s*)(\d{4})", r"\1'\2'", q)
    q = re.sub(r"(strftime\('%m',\s*[^)]+\)\s*=\s*)(\d{1,2})", lambda m: f"{m.group(1)}'{int(m.group(2)):02d}'", q)
    return q.strip()

def ask_agent(question):
    messages = [{"role": "user", "content": question}]
    functions = [
        {
            "name": "query_database",
            "description": "Run SQL query on orders database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "call_api_action",
            "description": "Trigger external API call",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "data": {"type": "object"}
                },
                "required": ["action", "data"]
            }
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        functions=functions,
        function_call="auto"
    )

    choice = response.choices[0]
    log_console(f"Agent choice: {choice.finish_reason}")

    if choice.finish_reason == "function_call":
        name = choice.message.function_call.name
        arguments = json.loads(choice.message.function_call.arguments)

        if name == "query_database":
            raw_query = arguments.get("query", "")
            query = normalize_sql(raw_query)
            log_console(f"Executing SQL: {query}")
            df = run_query(query)
            result = f"""### Query result

```sql
{query}
```
"""
            log_to_file(question, result)
            return result, df

        if name == "call_api_action":
            action = arguments.get("action")
            data = arguments.get("data")
            log_console(f"API called: {action} with data: {data}")
            result = f"📡 API triggered: `{action}` with data `{data}`"
            log_to_file(question, result)
            return result, pd.DataFrame([data])

    fallback = "Agent could not interpret the question."
    log_to_file(question, fallback)
    return fallback, None

st.set_page_config(page_title="Capstone Assistant")
st.title("📊 Capstone Business Assistant")

question = st.text_input("Ask a question about orders")

if st.button("Run"):
    if question:
        result, df = ask_agent(question)
        st.markdown(result)
        if isinstance(df, pd.DataFrame) and not df.empty:
            st.dataframe(df)
            st.session_state.df_result = df
else:
    df = st.session_state.get("df_result")

if isinstance(df, pd.DataFrame) and not df.empty:
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    file_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    st.download_button("📥 Download Excel", data=buffer, file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")