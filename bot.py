import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from config import BOT_TOKEN
from handlers.commands import (
    start,
    help_cmd,
    info_cmd,
    compare_cmd,
    top_cmd,
    setpref_cmd,
    myprefs_cmd,
    handle_text
)
from handlers.errors import error_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Запуск бота."""
    logger.info("Запуск бота...")

    # Создаем Updater и передаем ему токен бота
    updater = Updater(BOT_TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_cmd))
    dispatcher.add_handler(CommandHandler("info", info_cmd))
    dispatcher.add_handler(CommandHandler("compare", compare_cmd))
    dispatcher.add_handler(CommandHandler("top", top_cmd))
    dispatcher.add_handler(CommandHandler("setpref", setpref_cmd))
    dispatcher.add_handler(CommandHandler("myprefs", myprefs_cmd))

    # Регистрируем обработчик текстовых сообщений (кнопки)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    # Регистрируем обработчик ошибок
    dispatcher.add_error_handler(error_handler)

    # Запускаем бота
    logger.info("Бот запущен и готов к работе!")
    updater.start_polling()

    # Запускаем бота до тех пор, пока пользователь не нажмет Ctrl+C
    updater.idle()


if __name__ == "__main__":
    main()