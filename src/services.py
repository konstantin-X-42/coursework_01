import logging
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

#--------------------------------------------------
#----- 5. Веб страницы---ОСНОВНАЯ--API-------------
#--------------------------------------------------

# Настраиваем вывод логов прямо в консоль
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env в корне проекта
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("CURRENCY_API_KEY")
BASE_URL = "https://api.apilayer.com/exchangerates_data/convert"


def get_currency_rates(currencies: list[str]) -> list:
    """Принимает список валют (например, ['USD', 'EUR']) и возвращает

    список словарей с их курсами к рублю в формате:
    [{'currency': 'USD', 'rate': 91.5}, {'currency': 'EUR', 'rate': 98.2}]
    """
    if not currencies:
        logger.warning("Передан пустой список валют.")
        return []

    # Заглушка (офлайн-режим) на случай отсутствия ключа или сбоя сети
    mock_data = {"USD": 91.50, "EUR": 98.20, "RUB": 1.0}

    # 1. Проверка наличия API-ключа
    if not API_KEY:
        logger.error(
            "Критическая ошибка: API-ключ не найден в переменных окружения."
        )
        logger.warning("Переход в резервный офлайн-режим.")
        return [
            {"currency": cur, "rate": mock_data.get(cur, 75.0)}
            for cur in currencies
        ]

    rates_list = []
    headers = {"apikey": API_KEY}

    try:
        logger.info(f"Начало сетевого запроса курсов для валют: {currencies}")

        # Циклом проходим по каждой запрошенной валюте
        for cur in currencies:
            if cur == "RUB":
                rates_list.append({"currency": "RUB", "rate": 1.0})
                logger.info("Для валюты RUB автоматически установлен курс 1.0")
                continue

            # Запрашиваем стоимость ровно 1 единицы валюты к RUB
            params = {"to": "RUB", "from": cur, "amount": 1.0}

            response = requests.get(
                BASE_URL, headers=headers, params=params, timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                # Получаем результат конвертации и округляем до 2 знаков
                rate = round(float(data.get("result", 0.0)), 2)

                rates_list.append({"currency": cur, "rate": rate})
                logger.info(
                    f"Успешно получен курс {cur} через API"
                )
            else:
                logger.error(
                    f"Ошибка API для валюты {cur}. Статус-код: {response.status_code}. Ответ: {response.text}"
                )
                logger.warning(
                    f"Для валюты {cur} используются резервные данные."
                )
                rates_list.append(
                    {"currency": cur, "rate": mock_data.get(cur, 75.0)}
                )

        logger.info("Обработка всех валют успешно завершена.")
        return rates_list

    except (requests.RequestException, KeyError, ValueError) as e:
        logger.error(
            f"Произошел сетевой или системный сбой при запросе курсов: {e}"
        )
        logger.warning("Переход на резервные курсы для всего списка валют.")
        # В случае полного падения сети возвращаем заглушки для всего списка
        return [
            {"currency": cur, "rate": mock_data.get(cur, 75.0)}
            for cur in currencies
        ]


# ==========================================
# ЗАПУСК функции get_currency_rates()
# ==========================================
if __name__ == "__main__":

    # Передаем список валют, как в проекте
    test_currencies = ["USD", "EUR", "GBP"]

    result = get_currency_rates(test_currencies)

    print("\n--  -- Результат выполнения функции get_currency_rates() --  --")
    print(result)


# --------------------------------------------------------------------


API_KEY = os.getenv("MARKETSTACK_API_KEY")
BASE_URL = "https://api.marketstack.com/v1/eod"


def get_stock_prices(currencies: list[str]) -> list:
    """Запрос текущих цен акций в USD через бесплатный финансовый API.
    Принимает список тикеров акций (например, ['AAPL', 'AMZN'])
    и возвращает список словарей с их последней ценой закрытия (в USD).
    """
    if not currencies:
        logger.warning("Передан пустой список тикеров валют.")
        return []

    # Заглушка (офлайн-режим) на случай отсутствия ключа или сбоя сети
    mock_data = {
        "AAPL": 180.0,
        "AMZN": 175.0,
        "GOOGL": 150.0,
        "MSFT": 420.0,
        "TSLA": 170.0
    }

    if not API_KEY:
        logger.error("Критическая ошибка: API-ключ не найден в переменных окружения.")
        logger.warning("Переход в резервный офлайн-режим.")
        return [
            {"currency": cur, "rate": mock_data.get(cur, 100.0)}
            for cur in currencies
        ]

    # Переводим список тикеров в строку через запятую для Marketstack API
    symbols = ",".join(currencies)

    # Ключ в Marketstack передается как параметр access_key, а не в заголовках
    params = {
        "access_key": API_KEY,
        "symbols": symbols,
        "limit": len(currencies)  # Ограничиваем количество записей
    }

    logger.info(f"Начало сетевого запроса курсов ценных бумаг: {currencies}")

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()  # Вызовет ошибку при сбое сети или неверном токене

        data = response.json()
        stock_data = data.get("data", [])

        # Если сервер прислал пустой массив (например, из-за лимитов бесплатного тарифа)
        if not stock_data:
            logger.warning("API вернул пустой массив. Переход на резервные курсы ценных бумаг")
            return [
                {"currency": cur, "rate": mock_data.get(cur, 100.0)}
                for cur in currencies
            ]

        rates_list = []
        # Разбираем массив данных 'data' из ответа API
        for item in stock_data:
            ticker = item.get("symbol")
            # Берем цену закрытия (close)
            rate = round(float(item.get("close", 0.0)), 2)
            rates_list.append({"currency": ticker, "rate": rate})
            logger.info(f"Успешно получен курс {ticker} через API")

        logger.info("Обработка всех ценных бумаг успешно завершена.")
        return rates_list

    except (requests.RequestException, KeyError, ValueError) as e:
        logger.error(f"Произошел сетевой или системный сбой при запросе курсов ценных бумаг: {e}")
        logger.warning("Переход на резервные курсы для всего списка ценных бумаг.")
        # В случае полного падения сети возвращаем заглушки для всего списка
        return [
            {"currency": cur, "rate": mock_data.get(cur, 100.0)}
            for cur in currencies
        ]


# ==========================================================
# ЗАПУСК функции get_stock_prices()
# ==========================================================

if __name__ == "__main__":
    # Тестовый список обновлен в соответствии с вашим запросом
    test_currencies = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]

    try:
        result = get_stock_prices(test_currencies)
        print("\n-- -- Результат выполнения функции get_stock_prices() -- --")
        print(result)
    except Exception as e:
        print(f"\nПроизошла ошибка при выполнении: {e}")

#--------------------------------------------------
#----- 9. Сервисы---ОСНОВНАЯ-----------------------
#--------------------------------------------------

import json
import logging
from datetime import datetime
from functools import reduce

logger = logging.getLogger(__name__)


def analyze_cashback_categories(data: list[dict], year: int, month: int) -> str:
    """
    Анализирует транзакции за указанный год и месяц с использованием ФП.
    Рассчитывает потенциальный кешбэк (1% от суммы расходов) по каждой категории.
    Возвращает JSON-строку с результатами.
    """
    logger.info(f"Начало анализа категорий кешбэка за {month:02d}.{year}")

    if not data:
        logger.warning("Передан пустой список транзакций.")
        return json.dumps({}, ensure_ascii=False)

    # 1. ФП: Фильтрация транзакций по году, месяцу и знаку суммы (только расходы)
    def is_target_transaction(tx: dict) -> bool:
        try:
            # Парсим дату транзакции. Поддерживаем формат из Excel 'ДД.ММ.ГГГГ' или 'ГГГГ-ММ-ДД'
            tx_date_str = tx.get("Дата операции", "")
            if "-" in tx_date_str:
                dt = datetime.strptime(tx_date_str.split()[0], "%Y-%m-%d")
            else:
                dt = datetime.strptime(tx_date_str.split()[0], "%d.%m.%Y")

            amount = float(tx.get("Сумма платежа", 0))

            # Проверяем условия: нужный год, нужный месяц и это расход (сумма меньше 0)
            return dt.year == year and dt.month == month and amount < 0
        except (ValueError, TypeError, IndexError) as e:
            logger.debug(f"Пропущена некорректная транзакция: {tx}. Ошибка: {e}")
            return False

    filtered_transactions = list(filter(is_target_transaction, data))
    logger.info(f"Отфильтровано транзакций для анализа: {len(filtered_transactions)}")

    # 2. ФП: Агрегация данных с помощью reduce
    def accumulator(acc: dict, tx: dict) -> dict:
        category = tx.get("Категория", "Без категории")
        # Берем абсолютное значение расхода
        amount = abs(float(tx.get("Сумма платежа", 0)))

        # Кешбэк: 1 рубль на каждые 100 рублей расходов (1%)
        # Округляем до целых рублей для соответствия примеру из ТЗ
        cashback = int(amount // 100)

        acc[category] = acc.get(category, 0) + cashback
        return acc

    # Запуск сверки (reduce) с начальным пустым словарем
    category_cashback = reduce(accumulator, filtered_transactions, {})

    # Фильтруем категории, где кешбэк равен 0, чтобы не засорять вывод
    final_result = {k: v for k, v in category_cashback.items() if v > 0}

    logger.info("Анализ успешно завершен.")
    return json.dumps(final_result, ensure_ascii=False, indent=4)

#--------------------------------------------------
#----- 10. Сервисы---Доп Простой поиск-------------
#--------------------------------------------------

import json
import logging
import re


def simple_search(data: list[dict], search_query: str) -> str:
    """
    Ищет транзакции, содержащие поисковый запрос в описании или категории.
    Регистр символов не учитывается.
    """
    logger.info(f"Запуск простого поиска по запросу: '{search_query}'")

    if not search_query:
        logger.warning("Передан пустой поисковый запрос.")
        return json.dumps([], ensure_ascii=False)

    query_lower = search_query.lower()
    results = []

    for tx in data:
        # Приводим к строке и нижнему регистру для безопасного поиска
        category = str(tx.get("Категория", "")).lower()
        description = str(tx.get("Описание", "")).lower()

        if query_lower in category or query_lower in description:
            results.append(tx)

    logger.info(f"Простой поиск завершен. Найдено транзакций: {len(results)}")
    return json.dumps(results, ensure_ascii=False, indent=4)

# ==========================================
# ЗАПУСК функции simple_search()
# ==========================================

if __name__ == "__main__":
    # 1. Настраиваем логер (так как в начале файла вы написали logger = logging.getLogger(__name__))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    # 2. Создаем тестовые данные прямо внутри модуля
    mock_data = [
        {"Категория": "Супермаркеты", "Описание": "Покупка в Пятерочке", "Сумма": -1200},
        {"Категория": "ФаСТфУд", "Описание": "Обед в Бургер Кинг", "Сумма": -450},
        {"Категория": "Транспорт", "Описание": "Яндекс Такси", "Сумма": -350}
    ]

    print("\n--- ЗАПУСК ФУНКЦИИ    simple_search() ---")

    # 3. Вызываем функцию (импорт не нужен, мы уже находимся внутри этого файла)
    search_query = "фастфуд"
    json_result = simple_search(mock_data, search_query)

    print("\n=== РЕЗУЛЬТАТ РАБОТЫ ФУНКЦИИ ===")
    print(json_result)


# --------------------------------------------------------------------------

def search_by_phone_numbers(data: list[dict]) -> str:
    """
    Возвращает транзакции, содержащие в описании мобильные телефонные номера.
    Поддерживает форматы: +7 9XX XXX-XX-XX, +79XXXXXXXXX, 89XXXXXXXXX и т.д.
    """
    logger.info("Запуск поиска транзакций с мобильными номерами телефонов")

    # Регулярное выражение для поиска российских мобильных номеров (начинаются на +79 или 89)
    # Учитывает возможные пробелы и дефисы между цифрами
    phone_pattern = re.compile(r'(?:\+7|8)\s?9\d{2}\s?\d{3}[\s-]?\d{2}[\s-]?\d{2}')
    results = []

    for tx in data:
        description = str(tx.get("Описание", ""))

        # Если в описании найдено совпадение с паттерном
        if phone_pattern.search(description):
            results.append(tx)

    logger.info(f"Поиск по номерам завершен. Найдено транзакций: {len(results)}")
    return json.dumps(results, ensure_ascii=False, indent=4)


# ==========================================
# ЗАПУСК функции search_by_phone_numbers()
# ==========================================

if __name__ == "__main__":
    import logging

    # 1. Настраиваем вывод логов в консоль
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    # 2. Инициализируем тестовый список транзакций с разными форматами номеров
    mock_data = [
        {"Категория": "Переводы", "Описание": "Перевод Ивану по номеру +7 912 345-67-89 на карту", "Сумма": -1000},
        {"Категория": "Связь", "Описание": "Оплата телефона 89998887766 через приложение", "Сумма": -500},
        {"Категория": "Супермаркеты", "Описание": "Покупка в Пятерочке (номер чека 123456)", "Сумма": -1200},
        {"Категория": "Переводы", "Описание": "Перевод маме +79001234567", "Сумма": -2000},
        {"Категория": "Транспорт", "Описание": "Яндекс Такси, код подтверждения 8901", "Сумма": -350}
        # Не номер телефона
    ]

    print("\n--- ЗАПУСК ФУНКЦИИ    search_by_phone_numbers() ---")

    # 3. Вызываем функцию (импорты не нужны, мы внутри файла)
    json_result = search_by_phone_numbers(mock_data)

    print("\n=== РЕЗУЛЬТАТ РАБОТЫ ФУНКЦИИ ===")
    print(json_result)

#--------------------------------------------------
#----- 13. main------------------------------------
#--------------------------------------------------

import re

import re
import logging

# Настройка логгера для текущего модуля
logger = logging.getLogger(__name__)


def search_by_phone_numbers(data: list[dict]) -> list[dict]:
    """Возвращает транзакции, содержащие мобильные номера, включая форматы со скобками."""
    logger.info(f"Старт поиска транзакций по мобильным номерам. Всего на входе: {len(data)}")

    if not data:
        logger.warning("На вход передан пустой список транзакций.")
        return []

    # Шаблон находит +79..., 89..., +7 (900) 000-00-00, +7 900 000 00 00
    phone_pattern = re.compile(r'(?:\+7|8)[\s\-]?\(?9\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')

    result = []
    for tx in data:
        description = str(tx.get("Описание", ""))
        match = phone_pattern.search(description)

        if match:
            # Логируем на уровне DEBUG конкретный найденный номер для удобства отладки
            logger.debug(f"Найден номер телефона '{match.group()}' в транзакции ID: {tx.get('id', 'Не указан')}")
            result.append(tx)

    logger.info(f"Поиск завершен. Успешно найдено транзакций с номерами: {len(result)}")
    return result

# ==========================================
# ЗАПУСК функции search_by_phone_numbers()
# ==========================================
if __name__ == "__main__":
    print("=== ЗАПУСК ФУНКЦИИ ПОИСКА ПО ТЕЛЕФОНАМ    search_by_phone_numbers() ===\n")

    # Имитируем входящую базу транзакций
    transactions_pool = [
        {"id": 101, "Описание": "Перевод Ивану по номеру +7 912 345-67-89"},
        {"id": 102, "Описание": "Оплата мобильной связи 89998887766"},
        {"id": 103, "Описание": "Покупка в магазине Продукты"},
        {"id": 104, "Описание": "Звонок в техподдержку банка +7 (900) 123-45-67"}
    ]

    # Вызываем функцию
    filtered_transactions = search_by_phone_numbers(transactions_pool)

    print("\nРезультат фильтрации в памяти:")
    for tx in filtered_transactions:
        print(f" -> ID {tx['id']}: {tx['Описание']}")

    # Делаем быструю встроенную проверку (должно совпасть 3 транзакции из 4)
    assert len(filtered_transactions) == 3, f"Ошибка: ожидалось 3, найдено {len(filtered_transactions)}"
    print("\n=== ЛОКАЛЬНЫЙ ЗАПУСК УСПЕШНО ПРОЙДЕН ===")




############################
# def search_by_phone_numbers(data: list[dict]) -> list[dict]:
#     """Возвращает транзакции, содержащие мобильные номера, включая форматы со скобками."""
#     # Шаблон находит +79..., 89..., +7 (900) 000-00-00, +7 900 000 00 00
#     phone_pattern = re.compile(r'(?:\+7|8)[\s\-]?\(?9\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
#     return [tx for tx in data if phone_pattern.search(str(tx.get("Описание", "")))]
