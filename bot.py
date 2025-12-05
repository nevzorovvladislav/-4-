import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from config import BOT_TOKEN
from handlers.commands import (
    start,
    info_cmd,
    compare_cmd,
    top_cmd,
    setpref_cmd,
    myprefs_cmd,
)
from handlers.errors import error_handler

logging.basicConfig(level=logging.INFO)

def main():
    updater = Updater(token=BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("info", info_cmd))
    dp.add_handler(CommandHandler("compare", compare_cmd))
    dp.add_handler(CommandHandler("top", top_cmd))
    dp.add_handler(CommandHandler("setpref", setpref_cmd))
    dp.add_handler(CommandHandler("myprefs", myprefs_cmd))

    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
