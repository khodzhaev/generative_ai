import os
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Предопределенные стили
styles = [
    "cyberpunk",
    "watercolor painting",
    "pixel art",
    "3D render",
    "oil painting",
    "sketch drawing",
    "anime style",
    "photorealistic",
    "low-poly"
]

user_prompt = input("Введите ваш промпт: ")

output_dir = "images"
os.makedirs(output_dir, exist_ok=True)

for idx, style in enumerate(styles):
    prompt = f"{user_prompt}, in {style} style"
    print(f"🎨 Генерируем изображение в стиле: {style}...")

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        image_url = response.data[0].url

        import requests
        img_data = requests.get(image_url).content
        file_path = os.path.join(output_dir, f"{idx+1}_{style.replace(' ', '_')}.png")
        with open(file_path, 'wb') as handler:
            handler.write(img_data)

        print(f"✅ Сохранено: {file_path}")
        time.sleep(1.5)  
    except Exception as e:
        print(f"⚠️ Ошибка при генерации для {style}: {e}")
