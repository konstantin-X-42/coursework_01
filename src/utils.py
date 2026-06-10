import json
import logging
import os
from datetime import datetime

# --------------------------------------------------
# ----- 4. Веб страницы---ОСНОВНАЯ--API-------------
# --------------------------------------------------

# Настройка локального логгера для модуля утилит
logger = logging.getLogger(__name__)


def get_month_range(date_str: str) -> tuple[datetime, datetime]:
    """Вычисляет диапазон от 1-го числа месяца до указанной даты."""
    # Лог старта функции
    logger.info(f"Начало вызова get_month_range с параметром date_str='{date_str}'")

    if not date_str:
        logger.warning("Параметр date_str отсутствует или пустой")
        raise ValueError("Параметр даты обязателен")

    try:
        end_date = datetime.strptime(date_str, "%d.%m.%Y")
        start_date = end_date.replace(day=1)

        # Лог успешного вычисления
        logger.info(
            f"Успешно вычислен диапазон дат: {start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}"
        )
        return start_date, end_date

    except ValueError as e:
        # Логирование ошибки формата данных
        logger.error(f"Ошибка парсинга даты для значения '{date_str}': {e}")
        raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГГГ")


def load_user_settings(file_path: str) -> tuple[list[str], list[str]]:
    """Читает пользовательские настройки из JSON-файла."""
    # Лог старта функции
    logger.info(f"Начало вызова load_user_settings для пути: '{file_path}'")

    # Проверка физического наличия файла настроек
    if not os.path.exists(file_path):
        abs_path = os.path.abspath(file_path)
        logger.warning(
            f"Файл настроек не найден по пути: {abs_path}. Возвращаются дефолтные параметры."
        )
        return ["USD"], ["AAPL"]

    try:
        logger.info(f"Чтение конфигурационного файла: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        currencies = data.get("user_currencies", [])
        stocks = data.get("user_stocks", [])

        # Лог успешного извлечения данных
        logger.info(
            f"Настройки успешно загружены. Валюты: {currencies}, Акции: {stocks}"
        )
        return currencies, stocks

    except json.JSONDecodeError as e:
        # Логирование поврежденного JSON
        logger.error(
            f"Критическая ошибка: Файл {file_path} содержит некорректный формат JSON: {e}"
        )
        return ["USD"], ["AAPL"]

    except Exception as e:
        # Логирование системных сбоев (например, проблемы с правами доступа к файлу)
        logger.error(
            f"Непредвиденная ошибка при загрузке пользовательских настроек: {e}",
            exc_info=True,
        )
        return ["USD"], ["AAPL"]


# --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --
# --  --  -- ЗАПУСК ФУНКЦИИ -- get_month_range()  --  --  --  --  --  --  --  --
# --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --

# if __name__ == "__main__":
#     # 1. Тестируем получение диапазона дат
#     test_date = "15.12.2021"
#     print(f"--- Проверка функции get_month_range для даты {test_date} ---")
#     try:
#         start, end = get_month_range(test_date)
#         print(f"Начало периода: {start.strftime('%d.%m.%Y')}")
#         print(f"Конец периода: {end.strftime('%d.%m.%Y')}\n")
#     except ValueError as e:
#         print(f"Ошибка: {e}\n")
#
#     # 2. Тестируем чтение файла настроек
#     CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
#     settings_file = os.path.abspath(os.path.join(CURRENT_DIR, "..", "user_settings.json"))
#     # settings_file = "user_settings.json"
#     print(f"--- Проверка функции load_user_settings для файла {settings_file} ---")
#
#     currencies, stocks = load_user_settings(settings_file)
#     print(f"Загруженные валюты: {currencies}")
#     print(f"Загруженные акции: {stocks}")

# --------------------------------------------------
# ----- 6. Веб страницы---доп.ГЛАВНАЯ---------------
# --------------------------------------------------

# Настраиваем логирование, чтобы logger.info выводил сообщения в консоль
logging.basicConfig(level=logging.INFO)


def get_greeting(dt: datetime) -> str:
    """Возвращает приветствие строго по временным интервалам ТЗ."""
    logger.info(
        f"Начало определения приветствия для времени: {dt.strftime('%H:%M:%S')}"
    )

    time_now = dt.time()
    if (
        datetime.strptime("06:00", "%H:%M").time()
        <= time_now
        <= datetime.strptime("11:59", "%H:%M").time()
    ):
        greeting = "Доброе утро"
    elif (
        datetime.strptime("12:00", "%H:%M").time()
        <= time_now
        <= datetime.strptime("17:59", "%H:%M").time()
    ):
        greeting = "Добрый день"
    elif (
        datetime.strptime("18:00", "%H:%M").time()
        <= time_now
        <= datetime.strptime("22:59", "%H:%M").time()
    ):
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    logger.info(f"Успешно определено приветствие: '{greeting}'")
    return greeting


# ==========================================================
# ЗАПУСК функции get_greeting()
# ==========================================================
# if __name__ == "__main__":
#     # 1. Получаем текущую дату и время на компьютере
#     current_datetime = datetime.now()
#
#     # 2. Передаем её в функцию и получаем приветствие
#     greeting = get_greeting(current_datetime)
#
#     # 3. Выводим результат в консоль
#     print(f"Текущее время: {current_datetime.strftime('%H:%M:%S')}")
#     print(f"Результат: {greeting}")


def parse_incoming_datetime(date_str: str) -> tuple[datetime, datetime]:
    """
    Парсит строку 'YYYY-MM-DD HH:MM:SS'.
    Возвращает объект даты и дату начала этого месяца.
    """
    # Логируем входные данные
    logger.info(f"Начало парсинга входящей строки даты: '{date_str}'")

    try:
        end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0)

        # Логируем успешный результат перед возвратом
        logger.info(f"Успешный парсинг. Диапазон: {start_date} -> {end_date}")
        return start_date, end_date

    except ValueError as e:
        # exc_info=True запишет в логи подробную техническую причину сбоя (traceback)
        logger.error(f"Ошибка парсинга даты {date_str}: {e}", exc_info=True)
        raise ValueError("Неверный формат. Используйте YYYY-MM-DD HH:MM:SS")
