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

# ==========================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ    get_currency_rates()
# ==========================================

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

# ==========================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ    get_stock_prices()
# ==========================================

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
import unittest
from unittest.mock import patch
from src.services import analyze_cashback_categories

class TestAnalyzeCashbackCategories(unittest.TestCase):

    def test_analyze_success(self):
        """Тест успешного анализа транзакций с правильной фильтрацией и расчётом кэшбэка."""
        mock_data = [
            # Подходящая транзакция (Супермаркеты): расход 10500, кэшбэк 105
            {"Дата операции": "15.12.2025", "Сумма платежа": -10500.0, "Категория": "Супермаркеты"},
            # Подходящая транзакция (Супермаркеты): расход 450, кэшбэк 4 (всего 109)
            {"Дата операции": "20.12.2025 14:00:00", "Сумма платежа": -450.0, "Категория": "Супермаркеты"},
            # Подходящая транзакция (Фастфуд): расход 1000, кэшбэк 10
            {"Дата операции": "2025-12-01", "Сумма платежа": -1000.0, "Категория": "Фастфуд"},
            # НЕ подходит: другой месяц (ноябрь)
            {"Дата операции": "30.11.2025", "Сумма платежа": -5000.0, "Категория": "Одежда"},
            # НЕ подходит: другой год (2024)
            {"Дата операции": "15.12.2024", "Сумма платежа": -3000.0, "Категория": "Аптеки"},
            # НЕ подходит: это доход (сумма больше 0)
            {"Дата операции": "05.12.2025", "Сумма платежа": 50000.0, "Категория": "Зарплата"},
            # Подходящая транзакция без категории (должна сгруппироваться в 'Без категории')
            {"Дата операции": "10.12.2025", "Сумма платежа": -500.0}
        ]

        # Запускаем анализ за декабрь 2025 года
        json_result = analyze_cashback_categories(mock_data, year=2025, month=12)
        result = json.loads(json_result)

        # Проверяем структуру и точные суммы кэшбэка (1% через целочисленное деление // 100)
        self.assertEqual(result["Супермаркеты"], 109)  # (10500 // 100) + (450 // 100) = 105 + 4 = 109
        self.assertEqual(result["Фастфуд"], 10)  # 1000 // 100 = 10
        self.assertEqual(result["Без категории"], 5)  # 500 // 100 = 5
        self.assertNotIn("Одежда", result)
        self.assertNotIn("Зарплата", result)

    def test_analyze_empty_data(self):
        """Тест передачи пустого списка транзакций."""
        json_result = analyze_cashback_categories([], year=2025, month=12)
        self.assertEqual(json_result, "{}")

    def test_analyze_zero_cashback_filtered(self):
        """Тест фильтрации категорий, где кэшбэк равен 0."""
        mock_data = [
            # Расход меньше 100 рублей дает 0 рублей кэшбэка
            {"Дата операции": "01.12.2025", "Сумма платежа": -50.0, "Категория": "Такси"}
        ]
        json_result = analyze_cashback_categories(mock_data, year=2025, month=12)

        # Категория 'Такси' не должна попасть в финальный JSON, так как кэшбэк равен 0
        self.assertEqual(json_result, "{}")

    @patch("src.reports.logger")
    def test_analyze_corrupted_transactions(self, mock_logger):
        """Тест устойчивости функции к битым и некорректным данным в транзакциях."""
        mock_data = [
            # Битая дата
            {"Дата операции": "не-дата", "Сумма платежа": -1000.0, "Категория": "Продукты"},
            # Вместо суммы — невалидная строка
            {"Дата операции": "12.12.2025", "Сумма платежа": "много", "Категория": "Продукты"},
            # Пропущенные ключевые поля
            {"Категория": "Продукты"}
        ]

        # Функция не должна упасть, битые транзакции просто пропускаются через блок try-except
        json_result = analyze_cashback_categories(mock_data, year=2025, month=12)
        self.assertEqual(json_result, "{}")


if __name__ == "__main__":
    unittest.main()


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

# ==========================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ    simple_search()
# ==========================================
import json
import unittest
from unittest.mock import patch

# Импортируем функцию из вашего модуля (замените src.services на ваш реальный путь)
from src.services import simple_search


class TestSimpleSearch(unittest.TestCase):

    def setUp(self):
        """Инициализация общего набора тестовых транзакций перед каждым тестом."""
        self.mock_data = [
            {"Категория": "Супермаркеты", "Описание": "Покупка в Пятерочке", "Сумма": -1200},
            {"Категория": "ФаСТфУд", "Описание": "Обед в Бургер Кинг", "Сумма": -450},
            {"Категория": "Транспорт", "Описание": "Яндекс Такси", "Сумма": -350},
            {"Категория": "Другое", "Описание": "Обычный текст без категорий", "Сумма": -100}
        ]

    @patch("src.services.logger")
    def test_simple_search_by_description(self, mock_logger):
        """Тест успешного поиска по части описания (регистронезависимо)."""
        # Ищем "пятер" в разном регистре
        json_result = simple_search(self.mock_data, "пЯтЕр")
        result = json.loads(json_result)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Описание"], "Покупка в Пятерочке")
        self.assertEqual(result[0]["Категория"], "Супермаркеты")

    @patch("src.services.logger")
    def test_simple_search_by_category(self, mock_logger):
        """Тест успешного поиска по категории (регистронезависимо)."""
        # Ищем "фастфуд", в данных категория записана как "ФаСТфУд"
        json_result = simple_search(self.mock_data, "фастфуд")
        result = json.loads(json_result)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Категория"], "ФаСТфУд")
        self.assertEqual(result[0]["Описание"], "Обед в Бургер Кинг")

    @patch("src.services.logger")
    def test_simple_search_empty_query(self, mock_logger):
        """Тест передачи пустого поискового запроса."""
        json_result = simple_search(self.mock_data, "")
        result = json.loads(json_result)

        # Должен вернуться пустой JSON-массив
        self.assertEqual(result, [])
        # Проверяем, что логер зафиксировал предупреждение
        mock_logger.warning.assert_called_with("Передан пустой поисковый запрос.")

    @patch("src.services.logger")
    def test_simple_search_no_results(self, mock_logger):
        """Тест ситуации, когда совпадений не найдено."""
        json_result = simple_search(self.mock_data, "Авиабилеты")
        result = json.loads(json_result)

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()

# ==========================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ    search_by_phone_numbers()
# ==========================================

import json
import unittest
from unittest.mock import patch

# Импортируем функцию из вашего модуля (замените src.services на ваш реальный путь)
from src.services import search_by_phone_numbers


class TestSearchByPhoneNumbers(unittest.TestCase):

    def setUp(self):
        """Инициализация тестовых транзакций перед каждым тестом."""
        self.mock_data = [
            {"Категория": "Переводы", "Описание": "Перевод Ивану по номеру +7 912 345-67-89 на карту"},
            {"Категория": "Связь", "Описание": "Оплата телефона 89998887766 через приложение"},
            {"Категория": "Переводы", "Описание": "Перевод маме +79001234567"},
            {"Категория": "Супермаркеты", "Описание": "Покупка в Пятерочке (номер чека 123456)"},
            {"Категория": "Транспорт", "Описание": "Яндекс Такси, код подтверждения 8901"}
        ]

    @patch("src.services.logger")
    def test_search_by_phone_numbers_success(self, mock_logger):
        """Тест успешного поиска транзакций с мобильными номерами."""
        # ИСПРАВЛЕНО: Функция возвращает список, json.loads больше не используем
        result = search_by_phone_numbers(self.mock_data)

        self.assertEqual(len(result), 3)

        descriptions = [tx.get("Описание", "") for tx in result]
        self.assertIn("Перевод Ивану по номеру +7 912 345-67-89 на карту", descriptions)
        self.assertIn("Оплата телефона 89998887766 через приложение", descriptions)
        self.assertIn("Перевод маме +79001234567", descriptions)

    @patch("src.services.logger")
    def test_search_by_phone_numbers_no_matches(self, mock_logger):
        """Тест ситуации, когда совпадений не найдено."""
        clear_data = [
            {"Категория": "Супермаркеты", "Описание": "Обычная покупка в магазине"},
            {"Категория": "Другое", "Описание": "Номер договора № 9876543210"}
        ]
        result = search_by_phone_numbers(clear_data)

        # ИСПРАВЛЕНО: Прямое сравнение со списком и удален аргумент second
        self.assertEqual(result, [])

    @patch("src.services.logger")
    def test_search_by_phone_numbers_empty_data(self, mock_logger):
        """Тест передачи пустого списка транзакций."""
        result = search_by_phone_numbers([])

        # ИСПРАВЛЕНО: Убран лишний аргумент second
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()

#--------------------------------------------------
#----- 13. main------search_by_phone_numbers()-----
#--------------------------------------------------

import pytest
from src.services import search_by_phone_numbers

@pytest.fixture
def sample_transactions():
    """Фикстура с разнообразными тестовыми транзакциями."""
    return [
        {"id": 1, "Описание": "Перевод Ивану по номеру +7 912 345-67-89 на карту"},
        {"id": 2, "Описание": "Оплата телефона 89998887766 через приложение"},
        {"id": 3, "Описание": "Перевод маме +7(900)123-45-67"},
        {"id": 4, "Описание": "Покупка в супермаркете Лента"},
        {"id": 5, "Описание": "Контакты поддержки: +7 495 123-45-67 (городской)"},
        {"id": 6, "Описание": "Перевод по номеру 9123456789 без семерки/восьмерки"},
        {"id": 7, "Описание": "Номер в тексте +7 999 111 22 33 разбит пробелами"},
        {"id": 8, "Описание": ""},  # Пустое описание
        {"id": 9, "Сумма": -100}  # Вообще нет ключа "Описание"
    ]


def test_search_by_phone_numbers_formats(sample_transactions):
    """Тест проверяет, что находятся все валидные форматы мобильных номеров."""
    result = search_by_phone_numbers(sample_transactions)

    # Должны найтись транзакции с ID: 1, 2, 3, 7
    assert len(result) == 4

    found_ids = [tx["id"] for tx in result]
    assert 1 in found_ids  # +7 912 345-67-89
    assert 2 in found_ids  # 89998887766
    assert 3 in found_ids  # +7(900)123-45-67
    assert 7 in found_ids  # +7 999 111 22 33


def test_search_by_phone_numbers_exclusions(sample_transactions):
    """Тест проверяет, что городские номера и неполные номера игнорируются."""
    result = search_by_phone_numbers(sample_transactions)
    found_ids = [tx["id"] for tx in result]

    assert 5 not in found_ids  # Код 495 (городской) должен отсекаться
    assert 6 not in found_ids  # Без +7 или 8 в начале не должно подходить


def test_search_by_phone_numbers_empty_data():
    """Тест сценария, когда на вход подан пустой список."""
    assert search_by_phone_numbers([]) == []
