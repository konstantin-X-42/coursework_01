#--------------------------------------------------
#----- 5. Веб страницы---ОСНОВНАЯ--API-------------
#--------------------------------------------------

import os
import requests
import logging

logger = logging.getLogger(__name__)


def get_currency_rates(currencies: list[str], apilayer_key: str = None) -> list:
    """
    Получает актуальные курсы валют к рублю через API Fixer на маркетплейсе APILayer.
    """
    if not currencies:
        return []

    # Приоритет аргументу, если он "demo" или пустой — пробуем взять из .env
    api_key = apilayer_key if apilayer_key and apilayer_key != "demo" else os.getenv("CURRENCY_API_KEY")

    if not api_key:
        logger.error("Критическая ошибка: API-ключ для APILayer не предоставлен и не найден в .env!")
        return _get_mock_currency_rates(currencies)

    # ПРАВИЛЬНЫЙ URL: используем эндпоинт fixer и явно задаем базовую валюту RUB
    # (Убедитесь, что ваш тарифный план на APILayer позволяет менять base на RUB)
    url = "https://apilayer.com"

    # Формируем список валют для запроса через запятую, например: "USD,EUR"
    symbols = ",".join(currencies)
    params = {
        "base": "RUB",
        "symbols": symbols
    }

    rates_list = []

    try:
        headers = {
            "apikey": api_key,
            "User-Agent": "Mozilla/5.0"
        }
        # Передаем url, заголовки и параметры (base и symbols)
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # API Fixer при base=RUB возвращает rates вида: {"USD": 0.011, "EUR": 0.010}
            rates = data.get("rates", {})

            for cur in currencies:
                if cur in rates and rates[cur] != 0:
                    # Так как база RUB, то 1 единица валюты cur = 1 / rate рублей
                    rate_to_rub = round(1 / rates[cur], 2)
                    rates_list.append({
                        "currency": cur,
                        "rate": rate_to_rub
                    })
                    logger.info(f"Успешно получен курс APILayer для {cur}: {rate_to_rub} руб.")

            if rates_list:
                return rates_list
        else:
            logger.error(f"APILayer вернул ошибку {response.status_code}: {response.text}")

    except Exception as e:
        logger.error(f"Ошибка получения курсов валют через APILayer: {e}")

    # Если что-то пошло не так, возвращаем заглушки
    return _get_mock_currency_rates(currencies)


def _get_mock_currency_rates(currencies: list[str]) -> list:
    """Вспомогательная функция для выдачи резервных данных валют"""
    logger.warning("Используются резервные курсы валют (офлайн-режим)")
    mock_rates = {"USD": 91.50, "EUR": 98.20}
    return [{"currency": cur, "rate": mock_rates.get(cur, 85.00)} for cur in currencies]


def get_stock_prices(stocks: list[str]) -> list:
    """Запрос текущих цен акций в USD через бесплатный финансовый API."""
    if not stocks:
        return []

    prices_list = []
    try:
        for stock in stocks:
            url = f"https://financialmodelingprep.com{stock}?apikey=demo"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    stock_info = data
                    price = round(float(stock_info.get("price", 0)), 2)
                    prices_list.append({"stock": stock, "price": price})

        if prices_list:
            return prices_list

    except Exception as e:
        logger.error(f"Ошибка получения цен акций через API: {e}")

    logger.warning("Используются резервные стоимости акций (офлайн-режим)")
    mock_prices = {"AAPL": 175.30, "AMZN": 180.50, "GOOGL": 152.10, "MSFT": 415.20, "TSLA": 170.80}
    return [{"stock": stock, "price": mock_prices.get(stock, 100.00)} for stock in stocks]

#--------------------------------------------------
#----- 7. Веб страницы---доп.ГЛАВНАЯ---------------
#--------------------------------------------------

# import logging
# import requests
#
# logger = logging.getLogger(__name__)
#
# def get_currency_rates(currencies: list[str]) -> list[dict]:
#     """Получает курсы валют относительно RUB в виде списка словарей."""
#     if not currencies:
#         return []
#     url = "https://er-api.com"
#     try:
#         logger.info(f"Запрос курсов валют для: {currencies}")
#         response = requests.get(url, timeout=5)
#         if response.status_code == 200:
#             rates = response.json().get("rates", {})
#             return [
#                 {"currency": cur, "rate": round(1 / rates[cur], 2)}
#                 for cur in currencies if cur in rates
#             ]
#     except Exception as e:
#         logger.error(f"Ошибка при получении курсов валют: {e}")
#     return [{"currency": cur, "rate": "Данные недоступны"} for cur in currencies]
#
# def get_stock_prices(stocks: list[str]) -> list[dict]:
#     """Получает цены акций с Yahoo Finance в виде списка словарей."""
#     if not stocks:
#         return []
#     tickers = ",".join(stocks)
#     url = f"https://yahoo.com{tickers}"
#     headers = {'User-Agent': 'Mozilla/5.0'}
#     try:
#         logger.info(f"Запрос цен акций для: {stocks}")
#         response = requests.get(url, headers=headers, timeout=5)
#         if response.status_code == 200:
#             results = response.json().get("quoteResponse", {}).get("result", [])
#             return [
#                 {"stock": item["symbol"], "price": item.get("regularMarketPrice")}
#                 for item in results
#             ]
#     except Exception as e:
#         logger.error(f"Ошибка при получении цен акций: {e}")
#     return [{"stock": stock, "price": "Данные недоступны"} for stock in stocks]

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

logger = logging.getLogger(__name__)


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

#--------------------------------------------------
#----- 13. main------------------------------------
#--------------------------------------------------

import re

def search_by_phone_numbers(data: list[dict]) -> list[dict]:
    """Возвращает транзакции, содержащие мобильные номера, включая форматы со скобками."""
    # Шаблон находит +79..., 89..., +7 (900) 000-00-00, +7 900 000 00 00
    phone_pattern = re.compile(r'(?:\+7|8)[\s\-]?\(?9\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
    return [tx for tx in data if phone_pattern.search(str(tx.get("Описание", "")))]

