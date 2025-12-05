import os
from dotenv import load_dotenv

# Явно указываем путь к .env (лежит в корне проекта)
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN не задан! "
        "Установите переменную окружения или создайте .env файл."
    )

PREFS_FILE = "user_prefs.json"
RESTCOUNTRIES_NAME_ENDPOINT = "https://restcountries.com/v3.1/name/{}"
RESTCOUNTRIES_ALL_ENDPOINT = "https://restcountries.com/v3.1/all"
