import logging
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def error_handler(update: Update, context: CallbackContext):
    logger.error("Ошибка: %s", context.error, exc_info=True)
    if update and update.message:
        update.message.reply_text(
            "❌ Произошла ошибка. Попробуйте снова или выберите другое действие.",
            reply_markup=None  # Можно добавить клавиатуру обратно
        )