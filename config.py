import os

# Загружаем токен из переменной окружения
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN не задан! "
        "Установите переменную окружения или создайте .env файл."
    )

PREFS_FILE = "user_prefs.json"
RESTCOUNTRIES_NAME_ENDPOINT = "https://restcountries.com/v3.1/name/{}"
RESTCOUNTRIES_ALL_ENDPOINT = "https://restcountries.com/v3.1/all"
