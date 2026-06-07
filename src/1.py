import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Автоматически находит файл .env в корне проекта
load_dotenv()

API_KEY = os.getenv("MARKETSTACK_API_KEY")
BASE_URL = "https://api.marketstack.com/v1/eod"


def get_stock_prices(currencies: list[str]) -> list:
    """Запрос текущих цен акций в USD через бесплатный финансовый API.
    Принимает список тикеров акций (например, ['AAPL', 'AMZN'])
    и возвращает список словарей с их последней ценой закрытия (в USD).
    """
    if not currencies:
        return []

    if not API_KEY:
        raise ValueError("Критическая ошибка: API-ключ не найден в переменных окружения.")

    # Переводим список тикеров в строку через запятую для Marketstack API
    symbols = ",".join(currencies)

    # Ключ в Marketstack передается как параметр access_key, а не в заголовках
    params = {
        "access_key": API_KEY,
        "symbols": symbols,
        "limit": len(currencies)  # Ограничиваем количество записей
    }

    response = requests.get(BASE_URL, params=params, timeout=5)
    response.raise_for_status()  # Вызовет ошибку при сбое сети или неверном токене

    data = response.json()
    rates_list = []

    # Разбираем массив данных 'data' из ответа API
    stock_data = data.get("data", [])
    for item in stock_data:
        ticker = item.get("symbol")
        # Берем цену закрытия (close)
        rate = round(float(item.get("close", 0.0)), 2)
        rates_list.append({"currency": ticker, "rate": rate})

    return rates_list

# ==========================================================
# ЗАПУСК функции get_stock_prices()
# ==========================================================

if __name__ == "__main__":
    # Тестовый список акций теперь отработает корректно
    test_currencies = ["AAPL", "AMZN", "MSFT"]

    try:
        result = get_stock_prices(test_currencies)
        print("\n-- -- Результат выполнения функции get_stock_prices() -- --")
        print(result)
    except Exception as e:
        print(f"\nПроизошла ошибка при выполнении: {e}")