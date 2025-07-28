
import streamlit as st
import re

# Заранее определенные опасные шаблоны prompt-инъекций
dangerous_patterns = [
    r"ignore.*previous.*instructions",
    r"reset.*context",
    r"send.*password",
    r"admin.*access",
    r"delete.*database",
    r"shutdown.*system",
    r"upload.*data",
    r"disable.*filter",
]

def is_prompt_safe(prompt):
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False, pattern
    return True, None

st.title("🛡️ Prompt Injection Defender")

user_input = st.text_area("Введите сообщение для LLM:")

if st.button("Отправить"):
    if not user_input.strip():
        st.warning("❗ Введите сообщение.")
    else:
        safe, pattern = is_prompt_safe(user_input)
        if safe:
            st.success("✅ Запрос безопасен. Можно отправлять в LLM.")
            st.write("🔁 Ответ модели: [пример ответа от LLM]")
        else:
            st.error(f"🚨 Опасный запрос! Обнаружен шаблон: `{pattern}`")
            st.stop()
