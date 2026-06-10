import json
import logging
import os

import pandas as pd

from src.services import get_currency_rates, get_stock_prices
from src.utils import (
    get_greeting,
    get_month_range,
    load_user_settings,
    parse_incoming_datetime,
)

# --------------------------------------------------
# ----- 1. Веб страницы---ОСНОВНАЯ------------------
# --------------------------------------------------
# запуск функций в модуле
# python -m src.views
# --------------------------------------------------

# Директория, где лежит текущий файл (src)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Поднимаемся на уровень выше в корень проекта и заходим в папку data
EXCEL_PATH = os.path.join(CURRENT_DIR, "../data", "operations.xlsx")


def analytics_view(date_param: str) -> dict:
    """Генерирует данные для ответа на основе переданной даты"""
    # Лог старта функции
    logging.info(f"Начало вызова analytics_view с параметром date_param='{date_param}'")

    if not date_param:
        logging.warning("Параметр date_param отсутствует или пустой")
        return {"error": "Параметр 'date' обязателен"}

    try:
        start_date, end_date = get_month_range(date_param)
        logging.info(
            f"Успешно вычислен диапазон дат: {start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}"
        )
    except ValueError as e:
        logging.error(
            f"Ошибка вычисления диапазона дат для значения '{date_param}': {e}"
        )
        return {"error": str(e)}

    # Проверка физического наличия Excel-файла
    if not os.path.exists(EXCEL_PATH):
        logging.error(f"Файл Excel не найден по пути: {os.path.abspath(EXCEL_PATH)}")
        return {"error": f"Файл не найден по пути: {os.path.abspath(EXCEL_PATH)}"}

    try:
        logging.info(f"Чтение данных из файла: {EXCEL_PATH}")
        # Чтение таблицы (требуется установленный openpyxl)
        df = pd.read_excel(EXCEL_PATH)

        # Конвертируем колонку дат. dayfirst=True корректно парсит российский формат
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

        # Настраиваем правую границу, чтобы захватить весь последний день месяца до 23:59:59
        end_date_full = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59)

        # Фильтрация по диапазону дат
        filtered_df = df[
            (df["Дата операции"] >= pd.to_datetime(start_date))
            & (df["Дата операции"] <= end_date_full)
        ]

        # Сортировка от новых к старым
        filtered_df = filtered_df.sort_values(by="Дата операции", ascending=False)

        # Превращаем даты обратно в строковый формат для JSON-ответа
        if not filtered_df.empty:
            filtered_df["Дата операции"] = filtered_df["Дата операции"].dt.strftime(
                "%d.%m.%Y %H:%M:%S"
            )

        # Заменяем пустые ячейки (NaN) на None, иначе json.dumps() выдаст ошибку float('NaN')
        filtered_df = filtered_df.replace({pd.NA: None, float("nan"): None})

        # Преобразуем DataFrame в список словарей
        payload = filtered_df.to_dict(orient="records")

        # Лог успешного завершения обработки данных
        logging.info(
            f"Данные успешно отфильтрованы. Найдено операций за период: {len(payload)}"
        )

    except Exception as e:
        logging.error(f"Критическая ошибка при обработке Excel: {e}", exc_info=True)
        return {"error": "Внутренняя ошибка обработки данных"}

    logging.info("Функция analytics_view успешно завершила работу")
    return {
        "status": "success",
        "input_date": date_param,
        "range_start": start_date.strftime("%d.%m.%Y"),
        "range_end": end_date.strftime("%d.%m.%Y"),
        "payload": payload,
    }


# --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --
# --  --  -- ЗАПУСК ФУНКЦИИ --  analytics_view()  --  --  --  --  --  --  --  --
# --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --

# if __name__ == "__main__":
#     # Настройка логирования, чтобы видеть возможные ошибки в консоли
#     logging.basicConfig(level=logging.INFO)
#
#     # Тестовая дата в формате, который ожидает ваша функция get_month_range
#     # (обычно это "YYYY-MM" или "DD.MM.YYYY" — укажите нужный вам формат)
#     test_date = "15.12.2021"
#
#     print(f"--- Запуск проверки функции analytics_view для даты: {test_date} ---")
#
#     # Вызываем функцию
#     result = analytics_view(test_date)
#
#     # Вывод результата в формате JSON
#     print(json.dumps(result, indent=4, ensure_ascii=False))


# --------------------------------------------------
# ----- 3. Веб страницы---ОСНОВНАЯ--API-------------
# --------------------------------------------------

# Автоматически определяем директорию текущего файла, чтобы избежать NameError
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к файлу настроек на уровень выше
SETTINGS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, "..", "user_settings.json"))


def generate_json_response(date_str: str) -> dict:
    """Генерирует данные по курсам валют и акциям на основе настроек пользователя"""

    logging.info(
        f"Начало вызова generate_json_response с параметром date_str='{date_str}'"
    )

    if not date_str:
        logging.warning("Параметр date_str отсутствует или пустой")
        return {"error": "Параметр даты обязателен"}

    # 1. Расчет диапазона дат
    try:
        start_date, end_date = get_month_range(date_str)
        logging.info(
            f"Успешно вычислен диапазон дат: {start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}"
        )
    except ValueError as e:
        logging.error(f"Ошибка вычисления диапазона дат для значения '{date_str}': {e}")
        return {"error": str(e)}

    # 2. Проверка физического наличия файла настроек
    if not os.path.exists(SETTINGS_FILE):
        logging.error(f"Файл настроек не найден по пути: {SETTINGS_FILE}")
        return {"error": f"Файл настроек не найден по пути: {SETTINGS_FILE}"}

    # 3. Загрузка настроек и API-ключа (все операции с файлом в одном блоке)
    try:
        # Извлекаем основные настройки через вашу утилиту
        currencies, stocks = load_user_settings(SETTINGS_FILE)

        # Читаем ключ из этого же файла без повторного вызова os.path
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings_data = json.load(f)
            apilayer_key = settings_data.get("apilayer_key", "demo")

        logging.info(
            f"Настройки успешно загружены. Валюты: {currencies}, Акции: {stocks}"
        )
    except json.JSONDecodeError as e:
        logging.error(f"Некорректный формат JSON в файле настроек: {e}")
        return {"error": "Файл настроек поврежден (неверный JSON)"}
    except Exception as e:
        logging.error(f"Ошибка загрузки пользовательских настроек: {e}")
        return {"error": f"Ошибка загрузки пользовательских настроек: {e}"}

    # 4. Запрос внешних API с защитой от сбоев
    try:
        currency_data = get_currency_rates(currencies)
    except Exception as e:
        logging.error(f"Ошибка получения курсов валют: {e}")
        currency_data = []

    try:
        stock_data = get_stock_prices(stocks)
    except Exception as e:
        logging.error(f"Критический сбой функции get_stock_prices: {e}")
        stock_data = []

    logging.info("Функция generate_json_response успешно завершила работу")

    # 5. Формирование структуры ответа
    return {
        "status": "success",
        "analysis_period": {
            "start": start_date.strftime("%d.%m.%Y"),
            "end": end_date.strftime("%d.%m.%Y"),
        },
        "currencies_exchange_rub": currency_data,
        "stock_prices_usd": stock_data,
    }


# --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --
# --  --  -- ЗАПУСК ФУНКЦИИ --  generate_json_response()  --  --  --  --  --  --
# --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --  --

# if __name__ == "__main__":
#     # Включаем вывод логов в консоль терминала
#     logging.basicConfig(level=logging.INFO)
#
#     test_date = "15.12.2021"
#     print(
#         f"\n--- Запуск проверки функции generate_json_response для даты: {test_date} ---\n"
#     )
#
#     # Вызываем функцию
#     result_data = generate_json_response(test_date)
#
#     # Печатаем итоговый JSON-словарь в терминал
#     print(json.dumps(result_data, indent=4, ensure_ascii=False))

# --------------------------------------------------
# ----- 8. Веб страницы---доп.ГЛАВНАЯ---------------
# --------------------------------------------------

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Пути к файлам относительно структуры проекта
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "../user_settings.json")
EXCEL_FILE = os.path.join(BASE_DIR, "../data", "operations.xlsx")


def generate_main_page_json(date_str: str) -> dict:
    """Главная функция генерации JSON-ответа для страницы 'Главная'"""
    logger.info(f"Начало генерации отчета для даты: {date_str}")

    try:
        start_date, end_date = parse_incoming_datetime(date_str)
    except ValueError as e:
        return {"error": str(e)}

    greeting = get_greeting(end_date)

    # --- БЛОК PANDAS: Анализ Excel ---
    cards_list = []
    top_transactions = []

    if os.path.exists(EXCEL_FILE):
        try:
            logger.info(f"Чтение файла данных: {EXCEL_FILE}")
            # Читаем Excel, преобразуем колонку с датой в тип datetime
            df = pd.read_excel(EXCEL_FILE)
            df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

            # Фильтруем данные: с 1-го числа месяца по входящую дату включительно
            mask = (df["Дата операции"] >= start_date) & (
                df["Дата операции"] <= end_date
            )
            df_filtered = df[mask].copy()

            # 1. Расчет по картам (только расходы/платежи, обычно это отрицательные или целевые суммы)
            # Предположим, расходы в колонке 'Сумма платежа' идут со знаком минус или фильтруются по типу
            # Для примера берем модуль расходов, если они отрицательные, либо просто фильтруем расходы:
            df_expenses = df_filtered[df_filtered["Сумма платежа"] < 0].copy()
            df_expenses["Сумма платежа"] = df_expenses["Сумма платежа"].abs()

            if not df_expenses.empty and "Номер карты" in df_expenses.columns:
                # Группируем по картам
                grouped = (
                    df_expenses.groupby("Номер карты")["Сумма платежа"]
                    .sum()
                    .reset_index()
                )
                for _, row in grouped.iterrows():
                    card_num = str(row["Номер карты"]).strip()
                    if card_num and card_num != "nan":
                        # Берем последние 4 знака (удаляем звездочки если они есть)
                        last_4 = card_num[-4:] if len(card_num) >= 4 else card_num
                        total_spent = round(float(row["Сумма платежа"]), 2)
                        # Кешбэк: 1 рубль на каждые 100 рублей расходов
                        cashback = round(total_spent / 100, 2)

                        cards_list.append(
                            {
                                "last_digits": last_4,
                                "total_spent": total_spent,
                                "cashback": cashback,
                            }
                        )

            # 2. Топ-5 транзакций по сумме платежа (по модулю или по абсолютной величине расходов)
            df_filtered["Abs_Amount"] = df_filtered["Сумма платежа"].abs()
            df_top = df_filtered.sort_values(by="Abs_Amount", ascending=False).head(5)

            for _, row in df_top.iterrows():
                top_transactions.append(
                    {
                        "date": row["Дата операции"].strftime("%d.%m.%Y"),
                        "amount": round(float(row["Сумма платежа"]), 2),
                        "category": str(row.get("Категория", "Без категории")),
                        "description": str(row.get("Описание", "")),
                    }
                )

        except Exception as e:
            logger.error(f"Ошибка обработки Excel: {e}")
    else:
        logger.warning(f"Файл {EXCEL_FILE} не найден. Payload пустой.")

    # --- БЛОК API: Валюты и Акции ---
    currencies, stocks = load_user_settings(SETTINGS_FILE)
    currency_rates = get_currency_rates(currencies)
    stock_prices = get_stock_prices(stocks)

    # --- Сборка финального JSON-ответа ---
    response = {
        "greeting": greeting,
        "cards": cards_list,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    logger.info("Генерация отчета успешно завершена.")
    return response


# --------------------------------------------------
# ----- 14. main------------------------------------
# --------------------------------------------------

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.abspath(os.path.join(BASE_DIR, "../user_settings.json"))
EXCEL_FILE = os.path.abspath(os.path.join(BASE_DIR, "../data", "operations.xlsx"))


def generate_main_page_data(date_str: str) -> dict:
    """Формирует данные для Главной страницы согласно описанию колонок"""
    logger.info(f"Старт генерации данных главной страницы для даты: {date_str}")

    try:
        start_date, end_date = parse_incoming_datetime(date_str)
    except ValueError as e:
        logger.error(f"Ошибка парсинга даты: {e}")
        return {"error": str(e)}

    greeting = get_greeting(end_date)
    cards_list = []
    top_transactions = []

    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE)
            df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)

            # Фильтруем успешные транзакции за указанный период
            mask = (
                (df["Дата операции"] >= start_date)
                & (df["Дата операции"] <= end_date)
                & (df["Статус"] == "OK")
            )
            df_filtered = df[mask].copy()

            # 1. Анализ карт (Только расходы)
            df_expenses = df_filtered[df_filtered["Сумма платежа"] < 0].copy()
            if not df_expenses.empty and "Номер карты" in df_expenses.columns:
                df_expenses["Сумма_abs"] = df_expenses["Сумма платежа"].abs()
                grouped = (
                    df_expenses.groupby("Номер карты")["Сумма_abs"].sum().reset_index()
                )

                for _, row in grouped.iterrows():
                    raw_card = (
                        str(row["Номер карты"]).split(".")[0].strip()
                    )  # Очищаем от .0 если float
                    if raw_card and raw_card != "nan":
                        last_4 = raw_card[-4:] if len(raw_card) >= 4 else raw_card
                        total_spent = round(float(row["Сумма_abs"]), 2)
                        cashback = round(total_spent / 100, 2)

                        cards_list.append(
                            {
                                "last_digits": last_4,
                                "total_spent": total_spent,
                                "cashback": cashback,
                            }
                        )

            # 2. Топ-5 транзакций по абсолютному значению расхода/дохода
            df_filtered["amount_abs"] = df_filtered["Сумма операции"].abs()
            df_top = df_filtered.sort_values(by="amount_abs", ascending=False).head(5)

            for _, row in df_top.iterrows():
                top_transactions.append(
                    {
                        "date": row["Дата операции"].strftime("%d.%m.%Y"),
                        "amount": round(float(row["Сумма операции"]), 2),
                        "category": str(row.get("Категория", "Без категории")),
                        "description": str(row.get("Описание", "")),
                    }
                )
        except Exception as e:
            logger.error(f"Ошибка обработки Excel-файла: {e}", exc_info=True)

    # 3. Сторонние сервисы (настройки, валюты, акции)
    try:
        currencies, stocks = load_user_settings(SETTINGS_FILE)
        currency_rates = get_currency_rates(currencies)
        stock_prices = get_stock_prices(stocks)
    except Exception as e:
        logger.error(f"Ошибка загрузки пользовательских настроек/курсов: {e}")
        currency_rates, stock_prices = [], []

    return {
        "greeting": greeting,
        "cards": cards_list,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
