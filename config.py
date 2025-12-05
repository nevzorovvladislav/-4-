import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("ОШИБКА: Токен бота не найден в файле .env!")
    exit(1)

PREFS_FILE = os.path.join(os.getcwd(), 'data', "user_prefs.json")
