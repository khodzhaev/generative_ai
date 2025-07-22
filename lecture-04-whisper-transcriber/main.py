import whisper
import os

AUDIO_FILE = "./ITPU_MS_Degree_Session_5_-_Generative_AI-20241213_153714-Meeting_Recording.mp3"

if not os.path.exists(AUDIO_FILE):
    print(f"⚠️ Файл {AUDIO_FILE} не найден. Пожалуйста, добавьте его в папку.")
    exit()

print("📥 Загружаем модель Whisper...")
model = whisper.load_model("base")

print(f"🎧 Обрабатываем аудиофайл: {AUDIO_FILE}")
result = model.transcribe(AUDIO_FILE)

with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])

print("\n✅ Транскрипция завершена. Результат сохранён в transcript.txt")
