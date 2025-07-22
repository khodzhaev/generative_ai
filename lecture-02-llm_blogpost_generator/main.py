import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("lesson-1-transcript.txt", "r", encoding="utf-8") as f:
    transcript = f.read()

max_input_chars = 10000
if len(transcript) > max_input_chars:
    transcript = transcript[:max_input_chars]

prompt = f"""Write a blog post with markdown formatting based on the following lecture transcript...

Transcript:
{transcript}
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a markdown blog post writer."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=2048
)

blog_post = response.choices[0].message.content

with open("README.md", "w", encoding="utf-8") as f:
    f.write(blog_post)

print("✅ Blog post generated and saved to README.md")
