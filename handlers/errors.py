import logging
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def error_handler(update: Update, context: CallbackContext):
    """Логирует ошибки, вызванные обработчиками."""
    logger.error("Ошибка при обработке запроса: %s", context.error, exc_info=True)
    if update and update.message:
        update.message.reply_text(
            "❌ Произошла ошибка. Попробуйте снова или выберите другое действие.",
            # Для возврата кнопок: reply_markup=get_main_keyboard()
        )