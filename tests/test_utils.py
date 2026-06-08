import datetime
import json
import unittest
from unittest.mock import mock_open, patch

import pytest

from src.utils import get_greeting, get_month_range, load_user_settings

# --------------------------------------------------
# ----- 4. Веб страницы---ОСНОВНАЯ--API-------------
# --------------------------------------------------
# запуск тестов
# pytest tests/test_utils.py
# --------------------------------------------------

# ==========================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ    get_month_range()
# ==========================================


def test_get_month_range_success():
    """1. Тест успешного вычисления диапазона дат для обычной даты"""
    start, end = get_month_range("15.12.2021")

    # Проверяем, что вернулись объекты datetime
    assert isinstance(start, datetime.datetime)
    assert isinstance(end, datetime.datetime)

    # Проверяем правильность дат
    assert start == datetime.datetime(2021, 12, 1)
    assert end == datetime.datetime(2021, 12, 15)


def test_get_month_range_first_day():
    """2. Тест диапазона, если передано первое число месяца"""
    start, end = get_month_range("01.05.2024")

    assert start == datetime.datetime(2024, 5, 1)
    assert end == datetime.datetime(2024, 5, 1)


@pytest.mark.parametrize(
    "invalid_date",
    [
        "32.12.2021",  # Несуществующий день
        "15-12-2021",  # Неверный разделитель
        "2021.12.15",  # Неверный порядок (ГГГГ.ММ.ДД)
        "строка",  # Вообще не дата
    ],
)
def test_get_month_range_invalid_format(invalid_date):
    """3. Тест, что функция выбрасывает ValueError при ошибках формата"""
    with pytest.raises(ValueError) as exc_info:
        get_month_range(invalid_date)

    assert str(exc_info.value) == "Неверный формат даты. Используйте ДД.ММ.ГГГГ"


def test_get_month_range_empty_date():
    """3.1 Тест обработки пустой строки даты по вашей новой логике с логированием"""
    with pytest.raises(ValueError) as exc_info:
        get_month_range("")

    assert str(exc_info.value) == "Параметр даты обязателен"


# ==========================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ    load_user_settings()
# ==========================================


def test_load_user_settings_file_not_exists():
    """4. Тест поведения функции, если файл настроек отсутствует (должен вернуть дефолты)"""
    # Имитируем, что файла не существует на диске
    with patch("os.path.exists", return_value=False):
        currencies, stocks = load_user_settings("non_existent_file.json")

        assert currencies == ["USD"]
        assert stocks == ["AAPL"]


def test_load_user_settings_success():
    """5. Тест успешного чтения корректного файла настроек"""
    # Создаем мок-данные, которые должен вернуть файл
    mock_data = json.dumps(
        {
            "user_currencies": ["USD", "EUR", "RUB"],
            "user_stocks": ["AAPL", "GOOGL", "MSFT"],
        }
    )

    # Имитируем, что файл существует и читаем наши мок-данные
    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=mock_data)
    ):
        currencies, stocks = load_user_settings("user_settings.json")

        assert currencies == ["USD", "EUR", "RUB"]
        assert stocks == ["AAPL", "GOOGL", "MSFT"]


def test_load_user_settings_empty_keys():
    """6. Тест ситуации, когда JSON корректный, но нужные ключи внутри отсутствуют"""
    mock_data = json.dumps({"some_other_key": "value"})

    with patch("os.path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=mock_data)
    ):
        currencies, stocks = load_user_settings("user_settings.json")

        # Проверяем, что вернулись пустые списки по дефолту из .get()
        assert currencies == []
        assert stocks == []


# --------------------------------------------------
# ----- 6. Веб страницы---доп.ГЛАВНАЯ---------------
# --------------------------------------------------

# ==========================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ    get_greeting()
# ==========================================


class TestGetGreeting(unittest.TestCase):

    def test_morning_border(self):
        """Проверка утреннего интервала (06:00 - 11:59)."""
        # Граница: ровно 06:00
        dt_start = datetime.datetime.strptime("06:00", "%H:%M")
        self.assertEqual(get_greeting(dt_start), "Доброе утро")

        # Граница: ровно 11:59
        dt_end = datetime.datetime.strptime("11:59", "%H:%M")
        self.assertEqual(get_greeting(dt_end), "Доброе утро")

    def test_afternoon_border(self):
        """Проверка дневного интервала (12:00 - 17:59)."""
        # Граница: ровно 12:00
        dt_start = datetime.datetime.strptime("12:00", "%H:%M")
        self.assertEqual(get_greeting(dt_start), "Добрый день")

        # Граница: ровно 17:59
        dt_end = datetime.datetime.strptime("17:59", "%H:%M")
        self.assertEqual(get_greeting(dt_end), "Добрый день")

    def test_evening_border(self):
        """Проверка вечернего интервала (18:00 - 22:59)."""
        # Граница: ровно 18:00
        dt_start = datetime.datetime.strptime("18:00", "%H:%M")
        self.assertEqual(get_greeting(dt_start), "Добрый вечер")

        # Граница: ровно 22:59
        dt_end = datetime.datetime.strptime("22:59", "%H:%M")
        self.assertEqual(get_greeting(dt_end), "Добрый вечер")

    def test_night_border(self):
        """Проверка ночного интервала (23:00 - 05:59)."""
        # Ночь: ровно 23:00
        dt_start = datetime.datetime.strptime("23:00", "%H:%M")
        self.assertEqual(get_greeting(dt_start), "Доброй ночи")

        # Ночь: ровно 00:00 (полночь)
        dt_midnight = datetime.datetime.strptime("00:00", "%H:%M")
        self.assertEqual(get_greeting(dt_midnight), "Доброй ночи")

        # Ночь: ровно 05:59
        dt_end = datetime.datetime.strptime("05:59", "%H:%M")
        self.assertEqual(get_greeting(dt_end), "Доброй ночи")


if __name__ == "__main__":
    unittest.main()
