import pytest
import pandas as pd
from datetime import datetime
from src.views import analytics_view

#--------------------------------------------------
#----- 1. Веб страницы---ОСНОВНАЯ------------------
#--------------------------------------------------
# запуск тестов analytics_view()
# pytest tests/test_views.py
#--------------------------------------------------

# Создаем тестовый набор данных, имитирующий Excel-файл
@pytest.fixture
def mock_excel_data():
    return pd.DataFrame([
        {
            "Дата операции": "15.12.2021 18:44:47",
            "Статус": "OK",
            "Сумма операции": -118.0,
            "Категория": "Фастфуд",
            "Кэшбэк": None
        },
        {
            "Дата операции": "20.12.2021 12:00:00",
            "Статус": "OK",
            "Сумма операции": -500.0,
            "Категория": "Транспорт",
            "Кэшбэк": 10.0
        },
        {
            "Дата операции": "05.01.2022 10:00:00",
            "Статус": "OK",
            "Сумма операции": -300.0,
            "Категория": "Супермаркеты",
            "Кэшбэк": None
        }
    ])


def test_analytics_view_success(monkeypatch, mock_excel_data):
    """Тест успешной фильтрации данных за указанный месяц"""
    # Подменяем функцию read_excel, чтобы она возвращала тестовый DataFrame
    monkeypatch.setattr(pd, "read_excel", lambda *args, **kwargs: mock_excel_data.copy())
    # Имитируем, что файл всегда физически существует для прохождения проверки os.path.exists
    monkeypatch.setattr("os.path.exists", lambda path: True)

    # Запрашиваем декабрь 2021 года
    result = analytics_view("31.12.2021")

    assert result["status"] == "success"
    assert result["range_start"] == "01.12.2021"
    assert result["range_end"] == "31.12.2021"

    # Должно вернуться 2 операции из 3 (январская отсекается)
    assert len(result["payload"]) == 2

    # Проверяем сортировку (от свежих к старым)
    assert result["payload"][0]["Дата операции"] == "20.12.2021 12:00:00"
    assert result["payload"][1]["Дата операции"] == "15.12.2021 18:44:47"

    # Проверяем, что Кэшбэк заменился на None (в JSON станет null)
    assert result["payload"][1]["Кэшбэк"] is None


def test_analytics_view_empty_param():
    """Тест поведения функции при пустом параметре даты"""
    result = analytics_view("")
    assert "error" in result
    assert result["error"] == "Параметр 'date' обязателен"


def test_analytics_view_file_not_found(monkeypatch):
    """Тест поведения функции, если файл Excel отсутствует"""
    # Имитируем отсутствие файла
    monkeypatch.setattr("os.path.exists", lambda path: False)

    result = analytics_view("15.12.2021")
    assert "error" in result
    assert "Файл не найден" in result["error"]

#--------------------------------------------------
#----- 3. Веб страницы---ОСНОВНАЯ--API-------------
#--------------------------------------------------

import json
import datetime  # Прямой импорт модуля решает проблему сборщика Python 3.14
import pytest
from unittest.mock import patch, mock_open

# Импортируем тестируемую функцию
from src.views import generate_json_response


@pytest.fixture
def mock_settings_json():
    """Фикстура для имитации содержимого файла настроек"""
    return json.dumps({
        "currencies": ["USD", "EUR"],
        "stocks": ["AAPL", "AMZN"],
        "apilayer_key": "test_api_key"
    })


def test_generate_json_response_success(mock_settings_json):
    """1. Тест успешного выполнения функции при корректных данных"""

    # Создаем объекты дат через модуль datetime
    mock_range = (datetime.datetime(2021, 12, 1), datetime.datetime(2021, 12, 15))

    mock_currency_data = [{"currency": "USD", "rate": 91.5}]
    mock_stock_data = [{"stock": "AAPL", "price": 175.3}]

    # Изолируем функцию от внешних вызовов и файлов
    with patch("src.views.get_month_range", return_value=mock_range), \
            patch("os.path.exists", return_value=True), \
            patch("src.views.load_user_settings", return_value=(["USD", "EUR"], ["AAPL", "AMZN"])), \
            patch("builtins.open", mock_open(read_data=mock_settings_json)), \
            patch("src.views.get_currency_rates", return_value=mock_currency_data) as mock_currency, \
            patch("src.views.get_stock_prices", return_value=mock_stock_data) as mock_stocks:
        result = generate_json_response("15.12.2021")

        # Проверка структуры финального словаря
        assert result["status"] == "success"
        assert result["analysis_period"]["start"] == "01.12.2021"
        assert result["analysis_period"]["end"] == "15.12.2021"
        assert result["currencies_exchange_rub"] == mock_currency_data
        assert result["stock_prices_usd"] == mock_stock_data

        # Проверка передачи API-ключа из конфига
        mock_currency.assert_called_once_with(["USD", "EUR"], "test_api_key")
        mock_stocks.assert_called_once_with(["AAPL", "AMZN"])


def test_generate_json_response_empty_date():
    """2. Тест проверки на пустую строку даты"""
    result = generate_json_response("")
    assert "error" in result
    assert result["error"] == "Параметр даты обязателен"


def test_generate_json_response_invalid_date_format():
    """3. Тест обработки ошибки некорректного формата даты"""
    with patch("src.views.get_month_range", side_effect=ValueError("Неверный формат даты")):
        result = generate_json_response("invalid-date")

        assert "error" in result
        assert "Неверный формат даты" in result["error"]


def test_generate_json_response_missing_settings_file():
    """4. Тест ситуации, когда файл настроек физически отсутствует на диске"""
    mock_range = (datetime.datetime(2021, 12, 1), datetime.datetime(2021, 12, 15))

    with patch("src.views.get_month_range", return_value=mock_range), \
            patch("os.path.exists", return_value=False):
        result = generate_json_response("15.12.2021")

        assert "error" in result
        assert "Файл настроек не найден" in result["error"]


def test_generate_json_response_corrupted_json():
    """5. Тест обработки ситуации, когда JSON-файл настроек поврежден"""
    mock_range = (datetime.datetime(2021, 12, 1), datetime.datetime(2021, 12, 15))

    with patch("src.views.get_month_range", return_value=mock_range), \
            patch("os.path.exists", return_value=True), \
            patch("src.views.load_user_settings", return_value=(["USD"], ["AAPL"])), \
            patch("builtins.open", mock_open(read_data="{broken json")):
        result = generate_json_response("15.12.2021")

        assert "error" in result
        assert "Файл настроек поврежден" in result["error"]


def test_generate_json_response_api_services_failure(mock_settings_json):
    """6. Тест устойчивости к падениям внешних API сервисов (Fault Tolerance)"""
    mock_range = (datetime.datetime(2021, 12, 1), datetime.datetime(2021, 12, 15))

    with patch("src.views.get_month_range", return_value=mock_range), \
            patch("os.path.exists", return_value=True), \
            patch("src.views.load_user_settings", return_value=(["USD"], ["AAPL"])), \
            patch("builtins.open", mock_open(read_data=mock_settings_json)), \
            patch("src.views.get_currency_rates", side_effect=Exception("API валют недоступно")), \
            patch("src.views.get_stock_prices", side_effect=Exception("API акций недоступно")):
        result = generate_json_response("15.12.2021")

        # Проверяем, что функция перехватила падения API и вернула пустые списки
        assert result["status"] == "success"
        assert result["currencies_exchange_rub"] == []
        assert result["stock_prices_usd"] == []


#--------------------------------------------------
#----- 8. Веб страницы---доп.ГЛАВНАЯ---------------
#--------------------------------------------------

import pytest
from datetime import datetime
from src.utils import get_greeting
from src.views import generate_main_page_json


def test_get_greeting():
    """Тестирование правильности приветствия по часам"""
    assert get_greeting(datetime(2023, 5, 20, 9, 0, 0)) == "Доброе утро"
    assert get_greeting(datetime(2023, 5, 20, 15, 0, 0)) == "Добрый день"
    assert get_greeting(datetime(2023, 5, 20, 20, 0, 0)) == "Добрый вечер"
    assert get_greeting(datetime(2023, 5, 20, 2, 0, 0)) == "Доброй ночи"


def test_generate_main_page_json_structure():
    """Тестирование структуры ответа главной функции"""
    result = generate_main_page_json("2021-12-21 13:00:00")

    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result
    assert result["greeting"] == "Добрый день"
