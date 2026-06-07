import unittest
import os
from unittest.mock import patch, Mock
import requests

from src.services import get_currency_rates
from src.services import get_stock_prices

#--------------------------------------------------
#----- 5. Веб страницы---ОСНОВНАЯ--API-------------
#--------------------------------------------------
# запуск тестов
# pytest tests/test_services.py
#--------------------------------------------------

class TestCurrencyRates(unittest.TestCase):

    @patch("src.services.API_KEY", "TEST_KEY")
    @patch("requests.get")
    def test_api_success(self, mock_get):
        """Тест успешного получения данных из API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 91.543}
        mock_get.return_value = mock_response

        result = get_currency_rates(["USD"])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["currency"], "USD")
        self.assertEqual(result[0]["rate"], 91.54)

    def test_rub_handling(self):
        """Тест обработки рубля (курс всегда должен быть 1.0)."""
        result = get_currency_rates(["RUB"])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["currency"], "RUB")
        self.assertEqual(result[0]["rate"], 1.0)

    def test_empty_list(self):
        """Тест передачи пустого списка валют."""
        result = get_currency_rates([])
        self.assertEqual(result, [])

    @patch("src.services.API_KEY", "TEST_KEY")
    @patch("requests.get")
    def test_api_error_response(self, mock_get):
        """Тест поведения, если API возвращает ошибку (например, 404 или 429)."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        # Ожидаем, что сработает ветка else и подставится значение из mock_data
        result = get_currency_rates(["USD"])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["currency"], "USD")
        self.assertEqual(result[0]["rate"], 91.5)

    @patch("src.services.API_KEY", "TEST_KEY")
    @patch("requests.get", side_effect=requests.RequestException("Network error"))
    def test_network_failure(self, mock_get):
        """Тест полного сбоя сети (срабатывает блок try-except)."""
        # Передаем валюту, которой нет в моках, чтобы проверить дефолтное значение 75.0
        result = get_currency_rates(["EUR", "GBP"])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["currency"], "EUR")
        self.assertEqual(result[0]["rate"], 98.2)  # Из mock_data
        self.assertEqual(result[1]["currency"], "GBP")
        self.assertEqual(result[1]["rate"], 75.0)  # Дефолт из dict.get()

    @patch("src.services.API_KEY", None)
    def test_no_api_key(self):
        """Тест отсутствия API-ключа (сразу уходит в резервный офлайн-режим)."""
        result = get_currency_rates(["USD"])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["currency"], "USD")
        self.assertEqual(result[0]["rate"], 91.5)

# ===================================================================================
# ===================================================================================

class TestStockPrices(unittest.TestCase):

    @patch("src.services.API_KEY", "TEST_MARKETSTACK_KEY")
    @patch("requests.get")
    def test_get_stock_prices_success(self, mock_get):
        """Тест успешного получения цен акций через API."""
        # Мокаем структуру ответа Marketstack API (поле 'data' со списком словарей)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"symbol": "AAPL", "close": 182.546},
                {"symbol": "AMZN", "close": 174.9}
            ]
        }
        mock_get.return_value = mock_response

        result = get_stock_prices(["AAPL", "AMZN"])

        # Проверяем структуру и округление цен до 2 знаков
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"currency": "AAPL", "rate": 182.55})
        self.assertEqual(result[1], {"currency": "AMZN", "rate": 174.9})

    def test_get_stock_prices_empty_list(self):
        """Тест передачи пустого списка тикеров."""
        result = get_stock_prices([])
        self.assertEqual(result, [])

    @patch("src.services.API_KEY", None)
    def test_get_stock_prices_no_api_key(self):
        """Тест логики при отсутствии API-ключа (переход на mock_data)."""
        result = get_stock_prices(["AAPL", "UNKNOWN"])

        # Должно вернуть заглушки: 180.0 для AAPL и 100.0 по умолчанию
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"currency": "AAPL", "rate": 180.0})
        self.assertEqual(result[1], {"currency": "UNKNOWN", "rate": 100.0})

    @patch("src.services.API_KEY", "TEST_MARKETSTACK_KEY")
    @patch("requests.get")
    def test_get_stock_prices_empty_api_data(self, mock_get):
        """Тест ситуации, когда API возвращает пустой массив 'data'."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        result = get_stock_prices(["GOOGL"])

        # Ожидаем переход на резервные данные mock_data
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"currency": "GOOGL", "rate": 150.0})

    @patch("src.services.API_KEY", "TEST_MARKETSTACK_KEY")
    @patch("requests.get")
    def test_get_stock_prices_api_error(self, mock_get):
        """Тест обработки исключения при ошибке HTTP (например, 401 или 429)."""
        # Настраиваем raise_for_status на вызов ошибки
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.RequestException("HTTP Error")
        mock_get.return_value = mock_response

        result = get_stock_prices(["MSFT"])

        # Проверяем, что блок except перехватил ошибку и вернул заглушку
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {"currency": "MSFT", "rate": 420.0})


if __name__ == "__main__":
    unittest.main()





#--------------------------------------------------
#----- 9. Сервисы---ОСНОВНАЯ-----------------------
#--------------------------------------------------

import json
import pytest
from src.services import analyze_cashback_categories

def test_analyze_cashback_categories_success():
    # Тестовый набор транзакций
    mock_data = [
        {"Дата операции": "15.12.2021 12:00:00", "Сумма платежа": -10050.0, "Категория": "Супермаркеты"},
        {"Дата операции": "20.12.2021 15:30:00", "Сумма платежа": -5000.0, "Категория": "Супермаркеты"},
        {"Дата операции": "21.12.2021 18:00:00", "Сумма платежа": -25000.0, "Категория": "Одежда"},
        {"Дата операции": "05.11.2021 10:00:00", "Сумма платежа": -3000.0, "Категория": "Супермаркеты"}, # Другой месяц
        {"Дата операции": "22.12.2021 09:00:00", "Сумма платежа": 1500.0, "Категория": "Супермаркеты"},  # Доход (не расход)
    ]

    # Вызываем функцию для Декабря 2021
    json_result = analyze_cashback_categories(mock_data, year=2021, month=12)
    result = json.loads(json_result)

    # Проверки результатов
    # Супермаркеты: |-10050| + |-5000| = 15050. Кешбэк (15050 // 100) = 150
    assert result.get("Супермаркеты") == 150
    # Одежда: |-25000| = 25000. Кешбэк (25000 // 100) = 250
    assert result.get("Одежда") == 250
    # Ноябрьская транзакция и доход не должны попасть в расчет
    assert len(result) == 2

def test_analyze_cashback_categories_empty():
    json_result = analyze_cashback_categories([], year=2021, month=12)
    assert json.loads(json_result) == {}

#--------------------------------------------------
#----- 10. Сервисы---Доп Простой поиск-------------
#--------------------------------------------------

import json
import pytest
from src.services import simple_search, search_by_phone_numbers


# Фикстура с тестовыми данными транзакций
@pytest.fixture
def sample_transactions():
    return [
        {"Категория": "Супермаркеты", "Описание": "Лента Супер", "Сумма платежа": -1500},
        {"Категория": "Фастфуд", "Описание": "Вкусно и точка", "Сумма платежа": -350},
        {"Категория": "Переводы", "Описание": "Я МТС +7 921 11-22-33", "Сумма платежа": -500},
        {"Категория": "Связь", "Описание": "Тинькофф Мобайл +7 995 555-55-55", "Сумма платежа": -400},
        {"Категория": "Переводы", "Описание": "Перевод маме", "Сумма платежа": -1000},
    ]


def test_simple_search_by_description(sample_transactions):
    """Проверка простого поиска по совпадению в описании (без учета регистра)."""
    json_res = simple_search(sample_transactions, "леНтА")
    res = json.loads(json_res)

    assert len(res) == 1
    assert res[0]["Описание"] == "Лента Супер"


def test_simple_search_by_category(sample_transactions):
    """Проверка простого поиска по совпадению в категории."""
    json_res = simple_search(sample_transactions, "Фастфуд")
    res = json.loads(json_res)

    assert len(res) == 1
    assert res[0]["Категория"] == "Фастфуд"


def test_simple_search_empty_query(sample_transactions):
    """Проверка поведения при пустом поисковом запросе."""
    json_res = simple_search(sample_transactions, "")
    assert json.loads(json_res) == []


def test_search_by_phone_numbers(sample_transactions):
    """Проверка фильтрации транзакций, содержащих телефонные номера."""
    json_res = search_by_phone_numbers(sample_transactions)
    res = json.loads(json_res)

    # Должно найти 2 транзакции (с МТС и Тинькофф Мобайл)
    assert len(res) == 2
    assert "МТС" in res[0]["Описание"]
    assert "Тинькофф" in res[1]["Описание"]

