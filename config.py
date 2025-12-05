import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# --- ОСНОВНЫЕ НАСТРОЙКИ ---
# Токен берется из файла .env (TELEGRAM_BOT_TOKEN=ВАШ_ТОКЕН)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("ОШИБКА: Токен бота не найден в файле .env!")
    exit(1)

# --- ПУТИ К ФАЙЛАМ ДАННЫХ ---
# Используем os.path.join для создания путей, чтобы код работал на любой ОС

# Путь к файлу для хранения настроек пользователей (используется в services/prefs.py)
PREFS_FILE = os.path.join(os.getcwd(), 'data', "user_prefs.json")

# Файл для локального кэша стран (используется в services/restcountries.py, хотя там
# вы жестко прописали "countries_data.json", мы используем его имя для ясности)
# Примечание: В вашем restcountries.py используется локальная переменная LOCAL_DATA_FILE = "countries_data.json"
# Этот файл должен лежать в корне проекта.