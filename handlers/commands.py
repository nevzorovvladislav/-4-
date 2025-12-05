import logging
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from services.restcountries import fetch_country_by_name, fetch_all_countries
from services.prefs import set_user_pref, get_user_prefs
from utils.formatting import format_country_info, build_top_df

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Привет! Я бот стран.\n"
        "Команды:\n"
        "/info <страна>\n"
        "/compare <A> | <B>\n"
        "/top <population|area> <N>\n"
        "/setpref <key> <value>\n"
        "/myprefs"
    )


def info_cmd(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text("Использование: /info <страна>")
        return

    query = " ".join(context.args)
    update.message.chat.send_action("typing")

    data = fetch_country_by_name(query)
    if not data:
        update.message.reply_text("Страна не найдена.")
        return

    update.message.reply_text(
        format_country_info(data),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=False
    )


def compare_cmd(update: Update, context: CallbackContext) -> None:
    raw = update.message.text.partition(" ")[2]
    if "|" not in raw:
        update.message.reply_text("Использование: /compare A | B")
        return

    left, _, right = raw.partition("|")
    c1 = fetch_country_by_name(left.strip())
    c2 = fetch_country_by_name(right.strip())

    if not c1 or not c2:
        update.message.reply_text("Не удалось найти одну или обе страны.")
        return

    name1 = c1.get("name", {}).get("common", left.strip())
    name2 = c2.get("name", {}).get("common", right.strip())

    pop1 = c1.get("population", 0)
    pop2 = c2.get("population", 0)
    area1 = c1.get("area", 0)
    area2 = c2.get("area", 0)

    msg = (
        f"*Сравнение {name1} и {name2}*\n"
        f"• Население: {pop1:_} vs {pop2:_}\n"
        f"• Площадь: {area1:_} vs {area2:_}"
    )
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


def top_cmd(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        update.message.reply_text("Использование: /top population 10")
        return

    metric = context.args[0].lower()
    if metric not in ("population", "area"):
        update.message.reply_text("Метрика должна быть: population или area")
        return

    try:
        n = int(context.args[1])
    except ValueError:
        update.message.reply_text("N должно быть числом.")
        return

    all_c = fetch_all_countries()
    if not all_c:
        update.message.reply_text("Не удалось получить список стран.")
        return

    df = build_top_df(all_c)
    df = df.sort_values(by=metric, ascending=False).head(n)

    text = f"*Топ {n} по {metric}*\n"
    for _, row in df.iterrows():
        text += f"{row['name']}: {row[metric]:_}\n"

    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


def setpref_cmd(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        update.message.reply_text("Использование: /setpref ключ значение")
        return

    key = context.args[0]
    value = " ".join(context.args[1:])

    set_user_pref(update.effective_user.id, key, value)
    update.message.reply_text(f"Сохранено: {key} = {value}")


def myprefs_cmd(update: Update, context: CallbackContext) -> None:
    prefs = get_user_prefs(update.effective_user.id)
    if not prefs:
        update.message.reply_text("У вас нет настроек.")
        return

    msg = "Ваши настройки:\n" + "\n".join(f"{k}: {v}" for k, v in prefs.items())
    update.message.reply_text(msg)
