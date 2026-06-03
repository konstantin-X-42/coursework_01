import os
from pathlib import Path

import requests
from dotenv import load_dotenv  # загружает переменные окружения из файла .env в систему

# Загружаем переменные окружения из .env в корне проекта
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("CURRENCY_API_KEY")
BASE_URL = "https://api.apilayer.com/exchangerates_data/convert"


def conversion_rub(amount: float, from_currency: str) -> float:
    """Конвертирует сумму из указанной валюты (USD/EUR) в RUB через API.
    Если валюта перевода уже RUB, возвращает сумму в формате float без запроса.
    Если API недоступно или ключ отсутствует, возвращает 0.0.
    """
    # 1. Быстрая проверка: если валюта уже рубли, приводим к float и возвращаем
    if from_currency == "RUB":
        return float(amount)

    # 2. Проверка наличия API-ключа
    if not API_KEY:
        print("Ошибка: API-ключ не найден в переменных окружения.")
        return 0.0

    # 3. Запрос к серверу для остальных валют
    headers = {"apikey": API_KEY}
    params = {"to": "RUB", "from": from_currency, "amount": amount}

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)  # type: ignore
        # print("Ответ сервера:", response.text)
        response.raise_for_status()
        data = response.json()

        # Предполагаем, что API возвращает результат в поле "result"
        return float(data.get("result", 0.0))

    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Ошибка при конвертации валюты: {e}")
        return 0.0


# -----------вызываем функцию------------
# print(conversion_rub(153.26, "USD"))
# print(conversion_rub(153.26, "RUB"))
# print(conversion_rub(153.26, "EUR"))
# print(conversion_rub(153.26, "GBP"))
