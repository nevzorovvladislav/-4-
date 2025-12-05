import logging
import random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from services.restcountries import fetch_country_by_name, fetch_all_countries
from services.prefs import set_user_pref, get_user_prefs
from utils.formatting import format_country_info, build_top_df

logger = logging.getLogger(__name__)


# Создаем клавиатуру для меню
def get_main_keyboard():
    keyboard = [
        ['🌍 Информация о стране', '🎲 Случайная страна'],
        ['📊 Сравнить страны', '🏆 Топ стран'],
        ['⚙️ Мои настройки', '❓ Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def start(update: Update, context: CallbackContext) -> None:
    try:
        welcome_text = (
            "🤖 Добро пожаловать в Country Bot!\n\n"
            "Я помогу вам узнать информацию о любой стране мира.\n\n"
            "Используйте кнопки меню ниже или команды:\n"
            "• /info <страна> - информация о стране\n"
            "• /compare <страна1> | <страна2> - сравнение\n"
            "• /top <population|area> <N> - топ стран\n"
            "• /random - случайная страна\n"
            "• /help - помощь\n\n"
            "Выберите действие:"
        )

        update.message.reply_text(
            welcome_text,
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")
        update.message.reply_text("Ошибка при запуске бота.")


def help_cmd(update: Update, context: CallbackContext) -> None:
    try:
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
            "4. Случайная страна\n"
            "   - Нажмите кнопку '🎲 Случайная страна'\n"
            "   - Или введите: /random\n\n"
            "5. Настройки\n"
            "   - /setpref <ключ> <значение> - сохранить настройку\n"
            "   - /myprefs - показать мои настройки\n\n"
            "Просто нажимайте на нужные кнопки! 👇"
        )

        update.message.reply_text(
            help_text,
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в help_cmd: {e}")


def info_cmd(update: Update, context: CallbackContext) -> None:
    try:
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
        logger.info(f"Поиск информации о стране: '{query}'")

        data = fetch_country_by_name(query)
        if not data:
            update.message.reply_text(
                f"Страна '{query}' не найдена. Попробуйте ещё раз.",
                reply_markup=get_main_keyboard()
            )
            return

        country_info = format_country_info(data)

        update.message.reply_text(
            country_info,
            reply_markup=get_main_keyboard(),
            disable_web_page_preview=False
        )

    except Exception as e:
        logger.error(f"Ошибка в info_cmd: {e}", exc_info=True)
        update.message.reply_text(
            "Ошибка при получении информации о стране.",
            reply_markup=get_main_keyboard()
        )


def compare_cmd(update: Update, context: CallbackContext) -> None:
    try:
        # Если команда вызвана через кнопку, ждем ввода стран
        if not context.args:
            update.message.reply_text(
                "Введите две страны через | (вертикальную черту):\n"
                "Например: Russia | Germany",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data['waiting_for'] = 'country_compare'
            return

        # Получаем строку для сравнения
        raw = " ".join(context.args) if context.args else update.message.text

        # Если команда была через /compare, убираем "/compare " из начала
        if raw.startswith('/compare '):
            raw = raw.replace('/compare ', '', 1)

        logger.info(f"Строка для сравнения: '{raw}'")

        if "|" not in raw:
            update.message.reply_text(
                "Использование: /compare A | B\nПример: /compare Russia | Germany",
                reply_markup=get_main_keyboard()
            )
            return

        # Разделяем по символу "|"
        parts = raw.split("|")
        if len(parts) != 2:
            update.message.reply_text(
                "Использование: /compare A | B\nПример: /compare Russia | Germany",
                reply_markup=get_main_keyboard()
            )
            return

        left = parts[0].strip()
        right = parts[1].strip()

        logger.info(f"Левая страна: '{left}', правая страна: '{right}'")

        if not left or not right:
            logger.warning(f"Пустые названия: left='{left}', right='{right}'")
            update.message.reply_text(
                "Ошибка: одна из стран не указана.\n"
                "Использование: /compare A | B\nПример: /compare Russia | Germany",
                reply_markup=get_main_keyboard()
            )
            return

        # Получаем данные о странах
        logger.info(f"Поиск страны: '{left}'")
        c1 = fetch_country_by_name(left)

        logger.info(f"Поиск страны: '{right}'")
        c2 = fetch_country_by_name(right)

        if not c1 or not c2:
            not_found = []
            if not c1:
                not_found.append(left)
                logger.warning(f"Страна '{left}' не найдена")
            if not c2:
                not_found.append(right)
                logger.warning(f"Страна '{right}' не найдена")

            update.message.reply_text(
                f"Не удалось найти страны: {', '.join(not_found)}\n"
                f"Проверьте названия и попробуйте снова.\n\n"
                f"Доступные страны: Russia, Germany, United States, China, India, Brazil, Japan, France, United Kingdom, Italy и другие.",
                reply_markup=get_main_keyboard()
            )
            return

        # Получаем названия стран
        name1 = c1.get("name", {})
        if isinstance(name1, dict):
            name1 = name1.get("common", left)
        else:
            name1 = str(name1)

        name2 = c2.get("name", {})
        if isinstance(name2, dict):
            name2 = name2.get("common", right)
        else:
            name2 = str(name2)

        # Получаем числовые данные
        pop1 = c1.get("population", 0)
        pop2 = c2.get("population", 0)
        area1 = c1.get("area", 0)
        area2 = c2.get("area", 0)

        # Форматируем сообщение
        msg = (
                f"📊 Сравнение {name1} и {name2}\n\n"
                f"• 👥 Население:\n"
                f"  {name1}: {pop1:,}".replace(",", "_") + "\n"
                f"  {name2}: {pop2:,}".replace(",", "_") + "\n\n"
                f"• 📏 Площадь (км²):\n"
                f"  {name1}: {area1:,}".replace(",", "_") + "\n"
                f"  {name2}: {area2:,}".replace(",", "_")
        )

        update.message.reply_text(
            msg,
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Сравнение успешно отправлено: {name1} vs {name2}")

    except Exception as e:
        logger.error(f"Ошибка в compare_cmd: {e}", exc_info=True)
        update.message.reply_text(
            "Ошибка при сравнении стран.",
            reply_markup=get_main_keyboard()
        )


def top_cmd(update: Update, context: CallbackContext) -> None:
    try:
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

        # Получаем список стран
        all_c = fetch_all_countries()

        if not all_c:
            logger.error("Не удалось получить список стран.")
            update.message.reply_text(
                "⚠️ Не удалось получить данные из базы стран.\n"
                "Попробуйте позже или используйте другие команды.",
                reply_markup=get_main_keyboard()
            )
            return

        # Строим DataFrame
        df = build_top_df(all_c)

        if df.empty:
            update.message.reply_text(
                "Не удалось обработать данные стран.",
                reply_markup=get_main_keyboard()
            )
            return

        # Сортируем и берем топ N
        df = df.sort_values(by=metric, ascending=False).head(n)

        metric_name = "населению" if metric == "population" else "площади"
        text = f"🏆 Топ {n} стран по {metric_name}\n\n"

        medals = ["🥇", "🥈", "🥉"]
        for i, (_, row) in enumerate(df.iterrows()):
            medal = medals[i] if i < 3 else f"{i + 1}."
            value = f"{row[metric]:,}".replace(",", "_")
            text += f"{medal} {row['name']}: {value}\n"

        update.message.reply_text(
            text,
            reply_markup=get_main_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка в top_cmd: {e}", exc_info=True)
        update.message.reply_text(
            "❌ Ошибка при формировании топа стран.\n"
            "Попробуйте снова или выберите другое действие.",
            reply_markup=get_main_keyboard()
        )


def random_cmd(update: Update, context: CallbackContext) -> None:
    """Показать случайную страну"""
    try:
        # Используем предопределенный список популярных стран для надежности
        popular_countries = [
            "Russia", "Germany", "United States", "China", "India",
            "Brazil", "Japan", "France", "United Kingdom", "Italy",
            "Canada", "Australia", "Spain", "Mexico", "South Korea",
            "Ukraine", "Poland", "Turkey", "Egypt", "Vietnam",
            "Thailand", "Netherlands", "Sweden", "Norway", "Switzerland",
            "Argentina", "Chile", "Colombia", "Peru", "Venezuela",
            "Indonesia", "Malaysia", "Philippines", "Singapore", "Saudi Arabia",
            "South Africa", "Nigeria", "Kenya", "Morocco", "Algeria"
        ]

        # Выбираем случайную страну
        random_country_name = random.choice(popular_countries)

        # Получаем данные о стране
        country_data = fetch_country_by_name(random_country_name)

        if not country_data:
            # Если не удалось получить данные о выбранной стране,
            # пробуем другую случайную страну из списка
            attempts = 0
            while attempts < 3 and not country_data:
                random_country_name = random.choice(popular_countries)
                country_data = fetch_country_by_name(random_country_name)
                attempts += 1

            # Если после 3 попыток данные не получены, используем резервную информацию
            if not country_data:
                # Отправляем простой ответ с названием страны
                update.message.reply_text(
                    f"🎲 *Случайная страна:* {random_country_name}\n\n"
                    f"К сожалению, не удалось загрузить подробную информацию о стране.\n"
                    f"Попробуйте команду /info {random_country_name}",
                    reply_markup=get_main_keyboard(),
                    parse_mode='Markdown'
                )
                return

        # Форматируем информацию о стране
        country_info = format_country_info(country_data)

        # Создаем чистое сообщение без технических деталей
        full_message = f"🎲 *Случайная страна:*\n\n{country_info}"

        update.message.reply_text(
            full_message,
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown',
            disable_web_page_preview=False
        )

    except Exception as e:
        logger.error(f"Ошибка в random_cmd: {e}", exc_info=True)

        # Более дружелюбное сообщение об ошибке
        update.message.reply_text(
            "🎲 К сожалению, не удалось получить случайную страну.\n"
            "Попробуйте ещё раз или используйте другую команду.",
            reply_markup=get_main_keyboard()
        )


def setpref_cmd(update: Update, context: CallbackContext) -> None:
    try:
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

    except Exception as e:
        logger.error(f"Ошибка в setpref_cmd: {e}")


def myprefs_cmd(update: Update, context: CallbackContext) -> None:
    try:
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

    except Exception as e:
        logger.error(f"Ошибка в myprefs_cmd: {e}")


# Обработчик текстовых сообщений (для кнопок)
def handle_text(update: Update, context: CallbackContext) -> None:
    try:
        text = update.message.text

        if text == '🌍 Информация о стране':
            info_cmd(update, context)

        elif text == '🎲 Случайная страна':
            random_cmd(update, context)

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
                    if not text.strip():
                        update.message.reply_text("Название страны не может быть пустым.")
                        return
                    context.args = [text]
                    info_cmd(update, context)
                    context.user_data.pop('waiting_for', None)

                elif waiting_for == 'country_compare':
                    if not text.strip():
                        update.message.reply_text("Ввод не может быть пустым.")
                        return
                    if "|" not in text:
                        update.message.reply_text(
                            "Пожалуйста, введите две страны через |\nПример: Russia | Germany"
                        )
                        return

                    # Устанавливаем аргументы как список с одним элементом - введенным текстом
                    context.args = [text]
                    compare_cmd(update, context)
                    context.user_data.pop('waiting_for', None)

                elif waiting_for == 'country_top':
                    if not text.strip():
                        update.message.reply_text("Ввод не может быть пустым.")
                        return
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
                update.message.reply_text(
                    "Я не понял ваш запрос. Пожалуйста, используйте кнопки меню или команды.",
                    reply_markup=get_main_keyboard()
                )

    except Exception as e:
        logger.error(f"Ошибка в handle_text: {e}")
        update.message.reply_text(
            "Ошибка при обработке сообщения.",
            reply_markup=get_main_keyboard()
        )