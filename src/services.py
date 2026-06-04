#--------------------------------------------------
#----- 5. Веб страницы---ОСНОВНАЯ--API-------------
#--------------------------------------------------

import requests

def get_currency_rates(currencies: list[str]) -> dict:
    """Запрос курсов валют."""
    if not currencies: return {}
    url = "https://er-api.com"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            rates = response.json().get("rates", {})
            return {cur: round(1 / rates[cur], 2) for cur in currencies if cur in rates}
    except Exception:
        pass
    return {cur: "Данные недоступны" for cur in currencies}

def get_stock_prices(stocks: list[str]) -> dict:
    """Запрос цен акций."""
    if not stocks: return {}
    tickers = ",".join(stocks)
    url = f"https://yahoo.com{tickers}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            results = response.json().get("quoteResponse", {}).get("result", [])
            return {item["symbol"]: item.get("regularMarketPrice") for item in results}
    except Exception:
        pass
    return {stock: "Данные недоступны" for stock in stocks}

#--------------------------------------------------
#----- 7. Веб страницы---доп.ГЛАВНАЯ---------------
#--------------------------------------------------

import logging
import requests

logger = logging.getLogger(__name__)

def get_currency_rates(currencies: list[str]) -> list[dict]:
    """Получает курсы валют относительно RUB в виде списка словарей."""
    if not currencies:
        return []
    url = "https://er-api.com"
    try:
        logger.info(f"Запрос курсов валют для: {currencies}")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            rates = response.json().get("rates", {})
            return [
                {"currency": cur, "rate": round(1 / rates[cur], 2)}
                for cur in currencies if cur in rates
            ]
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
    return [{"currency": cur, "rate": "Данные недоступны"} for cur in currencies]

def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Получает цены акций с Yahoo Finance в виде списка словарей."""
    if not stocks:
        return []
    tickers = ",".join(stocks)
    url = f"https://yahoo.com{tickers}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        logger.info(f"Запрос цен акций для: {stocks}")
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            results = response.json().get("quoteResponse", {}).get("result", [])
            return [
                {"stock": item["symbol"], "price": item.get("regularMarketPrice")}
                for item in results
            ]
    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {e}")
    return [{"stock": stock, "price": "Данные недоступны"} for stock in stocks]

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

