import logging
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Импорт конфигурации
try:
    from config import BOT_TOKEN
except ImportError:
    logger.error("Ошибка загрузки конфигурации")
    sys.exit(1)

# Импорт обработчиков
try:
    from handlers.commands import (
        start, help_cmd, info_cmd, compare_cmd,
        top_cmd, setpref_cmd, myprefs_cmd, handle_text,
        random_cmd
    )
    # ИСПРАВЛЕНИЕ: Заменено 'handlers.errors' на 'handlers.error'
    from handlers.errors import error_handler
except ImportError as e:
    logger.error(f"Ошибка загрузки обработчиков: {e}")
    sys.exit(1)


def main():
    """Запуск бота."""
    logger.info("=" * 50)
    logger.info("Запуск CountryBot...")

    if not BOT_TOKEN:
        logger.error("Токен бота не найден!")
        print("ERROR: Проверьте файл .env!")
        return

    try:
        # Создаем Updater
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        # Регистрируем обработчики
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_cmd))
        dispatcher.add_handler(CommandHandler("info", info_cmd))
        dispatcher.add_handler(CommandHandler("compare", compare_cmd))
        dispatcher.add_handler(CommandHandler("top", top_cmd))
        dispatcher.add_handler(CommandHandler("random", random_cmd))
        dispatcher.add_handler(CommandHandler("setpref", setpref_cmd))
        dispatcher.add_handler(CommandHandler("myprefs", myprefs_cmd))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

        # Обработчик ошибок
        dispatcher.add_error_handler(error_handler)

        # Запускаем
        logger.info("Бот запущен!")
        print("=" * 50)
        print("Бот запущен!")
        print("Проверьте команду /start")
        print("=" * 50)

        updater.start_polling()
        updater.idle()

    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()