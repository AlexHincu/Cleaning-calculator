from telegram import Update, ReplyKeyboardMarkup  # Импорт классов для работы с Telegram API
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes  # Импорт классов для управления событиями

# Функция для чтения токена из файла
def read_token_from_file():
    """
    Читает токен Telegram-бота из файла `st.cf`.
    Формат файла: строка "token=ВАШ_ТОКЕН".
    Возвращает токен как строку. Если токен не найден или формат файла некорректен, возвращает None.
    """
    try:
        with open("st.cf", "r") as file:  # Открываем файл для чтения
            content = file.read().strip()  # Читаем содержимое файла и удаляем пробелы/переводы строк
            if "=" in content:  # Проверяем, есть ли разделитель "="
                key, value = content.split("=", 1)  # Разделяем строку на ключ и значение
                if key == "token" and value.strip():  # Проверяем, что ключ "token" и значение не пустое
                    return value.strip()  # Возвращаем токен
        raise ValueError("Файл `st.cf` имеет некорректный формат.")  # Ошибка, если формат не соответствует
    except FileNotFoundError:
        print("Ошибка: файл `st.cf` не найден.")  # Ошибка, если файл не найден
    except ValueError as e:
        print(f"Ошибка при чтении токена: {e}")  # Ошибка формата файла
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")  # Любая другая ошибка
    return None  # Если токен не найден, возвращаем None

# Глобальная переменная для хранения введенной площади уборки
area = 0

# Создаем клавиатуру с командами
keyboard = [
    ["/start", "/input_area"],
    ["/general_cleaning", "/office_cleaning"],
    ["/cleaning_after_renovation", "/express_cleaning"],
    ["/stop_calculation"],
]
# Генерируем объект ReplyKeyboardMarkup с клавиатурой
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)  # Клавиатура с автоматическим масштабированием

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Приветствует пользователя и отображает главное меню с фиксированной клавиатурой.
    """
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:",  # Приветственное сообщение
        reply_markup=reply_markup  # Отображаем клавиатуру
    )

# Обработчик команды /input_area
async def input_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Предлагает пользователю ввести площадь уборки.
    """
    await update.message.reply_text(
        "Введите площадь уборки (в квадратных метрах):",  # Сообщение о вводе площади
        reply_markup=reply_markup  # Сохраняем клавиатуру
    )

# Обработчик текстовых сообщений (ввод площади)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает текстовые сообщения от пользователя.
    Проверяет, является ли введенное сообщение числом (площадью).
    """
    global area  # Используем глобальную переменную для хранения площади
    try:
        area = float(update.message.text)  # Преобразуем текст в число
        await update.message.reply_text(
            f"Площадь уборки установлена: {area} м². Выберите тип уборки:",  # Подтверждаем введенное значение
            reply_markup=reply_markup  # Сохраняем клавиатуру
        )
    except ValueError:
        # Сообщение об ошибке, если пользователь ввел не число
        await update.message.reply_text(
            "Ошибка: введите корректное число.",
            reply_markup=reply_markup  # Сохраняем клавиатуру
        )

# Обработчик команд для расчета стоимости уборки
async def calculate_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Рассчитывает стоимость уборки в зависимости от выбранного типа.
    Умножает площадь на фиксированную ставку для каждого типа уборки.
    """
    global area  # Используем глобальную переменную для площади
    command = update.message.text  # Получаем команду, вызвавшую обработчик

    if area <= 0:  # Проверяем, введена ли площадь
        await update.message.reply_text(
            "Сначала введите площадь уборки с помощью команды /input_area.",  # Напоминание ввести площадь
            reply_markup=reply_markup  # Сохраняем клавиатуру
        )
        return

    # Определяем стоимость в зависимости от команды
    if command == "/general_cleaning":
        cost = area * 45
    elif command == "/office_cleaning":
        cost = area * 35
    elif command == "/cleaning_after_renovation":
        cost = area * 40
    elif command == "/express_cleaning":
        cost = area * 50
    else:
        cost = 0  # Если команда не совпадает, стоимость равна 0

    # Отправляем результат пользователю
    await update.message.reply_text(
        f"Стоимость уборки: {cost} руб.",
        reply_markup=reply_markup  # Сохраняем клавиатуру
    )

# Обработчик команды /stop_calculation
async def stop_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Сбрасывает площадь уборки и возвращает пользователя в главное меню.
    """
    global area  # Используем глобальную переменную для площади
    area = 0  # Сбрасываем площадь
    await update.message.reply_text(
        "Работа остановлена. Вы возвращены в главное меню.",
        reply_markup=reply_markup  # Сохраняем клавиатуру
    )

# Главная функция для запуска приложения
def main():
    """
    Главная функция для инициализации и запуска Telegram-бота.
    """
    token = read_token_from_file()  # Считываем токен из файла
    if not token:  # Если токен отсутствует, завершаем выполнение
        print("Ошибка: токен не найден.")
        return

    # Создаем объект приложения Telegram
    application = Application.builder().token(token).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))  # Обработчик для команды /start
    application.add_handler(CommandHandler("input_area", input_area))  # Обработчик для команды /input_area
    application.add_handler(CommandHandler("general_cleaning", calculate_cost))  # Обработчик для General Cleaning
    application.add_handler(CommandHandler("office_cleaning", calculate_cost))  # Обработчик для Office Cleaning
    application.add_handler(CommandHandler("cleaning_after_renovation", calculate_cost))  # Cleaning after renovation
    application.add_handler(CommandHandler("express_cleaning", calculate_cost))  # Express cleaning
    application.add_handler(CommandHandler("stop_calculation", stop_calculation))  # Обработчик для команды /stop_calculation
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))  # Обработчик текстового ввода

    # Запуск приложения в режиме polling
    application.run_polling()

# Точка входа
if __name__ == "__main__":
    main()
