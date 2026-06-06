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



