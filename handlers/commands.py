import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from services.restcountries import fetch_country_by_name, fetch_all_countries
from services.prefs import set_user_pref, get_user_prefs
from utils.formatting import format_country_info, build_top_df

logger = logging.getLogger(__name__)


# Создаем клавиатуру для меню
def get_main_keyboard():
    keyboard = [
        ['🌍 Информация о стране'],
        ['📊 Сравнить страны', '🏆 Топ стран'],
        ['⚙️ Мои настройки', '❓ Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def start(update: Update, context: CallbackContext) -> None:
    welcome_text = (
        "🤖 Добро пожаловать в Country Bot!\n\n"
        "Я помогу вам узнать информацию о любой стране мира.\n\n"
        "Используйте кнопки меню ниже или команды:\n"
        "• /info <страна> - информация о стране\n"
        "• /compare <страна1> | <страна2> - сравнение\n"
        "• /top <population|area> <N> - топ стран\n"
        "• /help - помощь\n\n"
        "Выберите действие:"
    )

    update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )


def help_cmd(update: Update, context: CallbackContext) -> None:
    help_text = (
        "📚 Доступные команды:\n\n"
        "1. Информация о стране\n"
        "   - Нажмите кнопку '🌍 Информация о стране'\n"
        "   - Или введите: /info <название>\n"
        "   Пример: /info Russia\n\n"
        "2. Сравнение стран\n"
        "   - Нажмите кнопку '📊 Сравнить страны'\n"
        "   - Или введите: /compare <A> | <B>\n"
        "   Пример: /compare Russia | Germany\n\n"
        "3. Топ стран\n"
        "   - Нажмите кнопку '🏆 Топ стран'\n"
        "   - Или введите: /top <population|area> <N>\n"
        "   Пример: /top population 10\n\n"
        "4. Настройки\n"
        "   - /setpref <ключ> <значение> - сохранить настройку\n"
        "   - /myprefs - показать мои настройки\n\n"
        "Просто нажмите на нужную кнопку в меню! 👇"
    )

    update.message.reply_text(
        help_text,
        reply_markup=get_main_keyboard()
    )


def info_cmd(update: Update, context: CallbackContext) -> None:
    # Если команда вызвана через кнопку, ждем ввода страны
    if not context.args:
        update.message.reply_text(
            "Введите название страны:\n"
            "Например: Russia, Germany, Japan",
            reply_markup=ReplyKeyboardRemove()
        )
        # Сохраняем состояние для следующего сообщения
        context.user_data['waiting_for'] = 'country_info'
        return

    # Если страна указана в аргументах
    query = " ".join(context.args)
    update.message.chat.send_action("typing")

    data = fetch_country_by_name(query)
    if not data:
        update.message.reply_text(
            f"Страна '{query}' не найдена. Попробуйте ещё раз.",
            reply_markup=get_main_keyboard()
        )
        return

    update.message.reply_text(
        format_country_info(data),
        reply_markup=get_main_keyboard(),
        disable_web_page_preview=False
    )


def compare_cmd(update: Update, context: CallbackContext) -> None:
    # Если команда вызвана через кнопку, ждем ввода стран
    if not context.args:
        update.message.reply_text(
            "Введите две страны через | (вертикальную черту):\n"
            "Например: Russia | Germany",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['waiting_for'] = 'country_compare'
        return

    raw = update.message.text.partition(" ")[2]
    if "|" not in raw:
        update.message.reply_text(
            "Использование: /compare A | B\nПример: /compare Russia | Germany",
            reply_markup=get_main_keyboard()
        )
        return

    left, _, right = raw.partition("|")
    c1 = fetch_country_by_name(left.strip())
    c2 = fetch_country_by_name(right.strip())

    if not c1 or not c2:
        update.message.reply_text(
            "Не удалось найти одну или обе страны. Проверьте названия.",
            reply_markup=get_main_keyboard()
        )
        return

    name1 = c1.get("name", {}).get("common", left.strip())
    name2 = c2.get("name", {}).get("common", right.strip())

    pop1 = c1.get("population", 0)
    pop2 = c2.get("population", 0)
    area1 = c1.get("area", 0)
    area2 = c2.get("area", 0)

    # УБРАЛИ MARKDOWN РАЗМЕТКУ
    msg = (
        f"📊 Сравнение {name1} и {name2}\n\n"
        f"• 👥 Население:\n"
        f"  {name1}: {pop1:_}\n"
        f"  {name2}: {pop2:_}\n\n"
        f"• 📏 Площадь (км²):\n"
        f"  {name1}: {area1:_}\n"
        f"  {name2}: {area2:_}"
    )
    update.message.reply_text(
        msg,
        reply_markup=get_main_keyboard()
    )


def top_cmd(update: Update, context: CallbackContext) -> None:
    # Если команда вызвана через кнопку, ждем ввод параметров
    if not context.args:
        update.message.reply_text(
            "Введите параметры для топа:\n"
            "Например: population 10\n"
            "Доступные метрики: population (население), area (площадь)",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['waiting_for'] = 'country_top'
        return

    if len(context.args) < 2:
        update.message.reply_text(
            "Использование: /top <population|area> <N>\nПример: /top population 10",
            reply_markup=get_main_keyboard()
        )
        return

    metric = context.args[0].lower()
    if metric not in ("population", "area"):
        update.message.reply_text(
            "Метрика должна быть: population (население) или area (площадь)",
            reply_markup=get_main_keyboard()
        )
        return

    try:
        n = int(context.args[1])
        if n <= 0 or n > 50:
            update.message.reply_text(
                "Введите число от 1 до 50",
                reply_markup=get_main_keyboard()
            )
            return
    except ValueError:
        update.message.reply_text(
            "N должно быть числом",
            reply_markup=get_main_keyboard()
        )
        return

    update.message.chat.send_action("typing")
    all_c = fetch_all_countries()
    if not all_c:
        update.message.reply_text(
            "Не удалось получить список стран.",
            reply_markup=get_main_keyboard()
        )
        return

    df = build_top_df(all_c)
    df = df.sort_values(by=metric, ascending=False).head(n)

    metric_name = "населению" if metric == "population" else "площади"
    text = f"🏆 Топ {n} стран по {metric_name}\n\n"

    medals = ["🥇", "🥈", "🥉"]
    for i, (_, row) in enumerate(df.iterrows()):
        medal = medals[i] if i < 3 else f"{i + 1}."
        value = f"{row[metric]:_,}"
        text += f"{medal} {row['name']}: {value}\n"

    update.message.reply_text(
        text,
        reply_markup=get_main_keyboard()
    )


def setpref_cmd(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        update.message.reply_text(
            "Использование: /setpref <ключ> <значение>\nПример: /setpref currency USD",
            reply_markup=get_main_keyboard()
        )
        return

    key = context.args[0]
    value = " ".join(context.args[1:])

    set_user_pref(update.effective_user.id, key, value)
    update.message.reply_text(
        f"✅ Настройка сохранена:\n{key} = {value}",
        reply_markup=get_main_keyboard()
    )


def myprefs_cmd(update: Update, context: CallbackContext) -> None:
    prefs = get_user_prefs(update.effective_user.id)
    if not prefs:
        update.message.reply_text(
            "У вас нет сохраненных настроек.",
            reply_markup=get_main_keyboard()
        )
        return

    msg = "⚙️ Ваши настройки:\n\n"
    for k, v in prefs.items():
        msg += f"• {k}: {v}\n"

    update.message.reply_text(
        msg,
        reply_markup=get_main_keyboard()
    )


# Обработчик текстовых сообщений (для кнопок)
def handle_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if text == '🌍 Информация о стране':
        info_cmd(update, context)

    elif text == '📊 Сравнить страны':
        compare_cmd(update, context)

    elif text == '🏆 Топ стран':
        top_cmd(update, context)

    elif text == '⚙️ Мои настройки':
        myprefs_cmd(update, context)

    elif text == '❓ Помощь':
        help_cmd(update, context)

    else:
        # Проверяем, ждем ли мы ввод от пользователя
        if 'waiting_for' in context.user_data:
            waiting_for = context.user_data['waiting_for']

            if waiting_for == 'country_info':
                # Обрабатываем ввод страны для информации
                context.args = [text]
                info_cmd(update, context)
                context.user_data.pop('waiting_for', None)

            elif waiting_for == 'country_compare':
                # Обрабатываем ввод стран для сравнения
                if "|" not in text:
                    update.message.reply_text(
                        "Пожалуйста, введите две страны через |\nПример: Russia | Germany"
                    )
                    return
                context.args = [text]
                compare_cmd(update, context)
                context.user_data.pop('waiting_for', None)

            elif waiting_for == 'country_top':
                # Обрабатываем ввод для топа
                parts = text.split()
                if len(parts) != 2:
                    update.message.reply_text(
                        "Введите две части: метрику и число\nПример: population 10"
                    )
                    return
                context.args = parts
                top_cmd(update, context)
                context.user_data.pop('waiting_for', None)

        else:
            # Если это неизвестный текст
            update.message.reply_text(
                "Я не понял ваш запрос. Пожалуйста, используйте кнопки меню или команды.",
                reply_markup=get_main_keyboard()
            )