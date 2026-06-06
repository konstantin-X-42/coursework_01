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

# Создаем тестовый набор данных, имитирующий ваш Excel-файл
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
    # Подменяем функцию read_excel, чтобы она возвращала наш тестовый DataFrame
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
#----- 8. Веб страницы---доп.ГЛАВНАЯ---------------
#--------------------------------------------------

import pytest
from datetime import datetimeй
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


