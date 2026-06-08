from datetime import datetime

import pandas as pd
import pytest

from src.views import analytics_view

# --------------------------------------------------
# ----- 1. Веб страницы---ОСНОВНАЯ------------------
# --------------------------------------------------
# запуск тестов analytics_view()
# pytest tests/test_views.py
# --------------------------------------------------


# Создаем тестовый набор данных, имитирующий Excel-файл
@pytest.fixture
def mock_excel_data():
    return pd.DataFrame(
        [
            {
                "Дата операции": "15.12.2021 18:44:47",
                "Статус": "OK",
                "Сумма операции": -118.0,
                "Категория": "Фастфуд",
                "Кэшбэк": None,
            },
            {
                "Дата операции": "20.12.2021 12:00:00",
                "Статус": "OK",
                "Сумма операции": -500.0,
                "Категория": "Транспорт",
                "Кэшбэк": 10.0,
            },
            {
                "Дата операции": "05.01.2022 10:00:00",
                "Статус": "OK",
                "Сумма операции": -300.0,
                "Категория": "Супермаркеты",
                "Кэшбэк": None,
            },
        ]
    )


def test_analytics_view_success(monkeypatch, mock_excel_data):
    """Тест успешной фильтрации данных за указанный месяц"""
    # Подменяем функцию read_excel, чтобы она возвращала тестовый DataFrame
    monkeypatch.setattr(
        pd, "read_excel", lambda *args, **kwargs: mock_excel_data.copy()
    )
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


# --------------------------------------------------
# ----- 3. Веб страницы---ОСНОВНАЯ--API-------------
# --------------------------------------------------

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Замените 'src.views' на ваш реальный путь импорта, если он отличается
from src.views import generate_json_response


@pytest.fixture
def mock_dependencies():
    """Фикстура для изоляции внешних функций, путей и файлов функции generate_json_response."""
    with patch("src.views.get_month_range") as mock_range, patch(
        "src.views.os.path.exists"
    ) as mock_exists, patch(
        "src.views.load_user_settings"
    ) as mock_load_settings, patch(
        "src.views.open", create=True
    ) as mock_open, patch(
        "src.views.get_currency_rates"
    ) as mock_currency, patch(
        "src.views.get_stock_prices"
    ) as mock_stock, patch(
        "src.views.logging"
    ):  # Отключаем логирование, чтобы не спамить в консоль

        # Задаем дефолтные значения для успешного прохождения сценариев
        mock_range.return_value = (datetime(2023, 10, 1), datetime(2023, 10, 31))
        mock_exists.return_value = True
        mock_load_settings.return_value = (["USD", "EUR"], ["AAPL", "GOOGL"])

        # Настраиваем фейковый контекстный менеджер для open()
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_open.return_value = mock_file

        # Мокаем работу json.load, который вызывается внутри open()
        with patch("src.views.json.load") as mock_json_load:
            mock_json_load.return_value = {
                "currencies": ["USD", "EUR"],
                "stocks": ["AAPL", "GOOGL"],
                "apilayer_key": "test_api_key",
            }

            yield {
                "range": mock_range,
                "exists": mock_exists,
                "load_settings": mock_load_settings,
                "currency": mock_currency,
                "stock": mock_stock,
                "json_load": mock_json_load,
            }


def test_generate_json_response_success(mock_dependencies):
    """Тест успешного выполнения функции при корректных данных."""
    # Настраиваем возвращаемые данные от внешних сервисов
    mock_dependencies["currency"].return_value = [{"currency": "USD", "rate": 90.0}]
    mock_dependencies["stock"].return_value = [{"stock": "AAPL", "price": 180.0}]

    response = generate_json_response("10.2023")

    # Проверяем структуру ответа
    assert response["status"] == "success"
    assert response["analysis_period"] == {"start": "01.10.2023", "end": "31.10.2023"}
    assert response["currencies_exchange_rub"] == [{"currency": "USD", "rate": 90.0}]
    assert response["stock_prices_usd"] == [{"stock": "AAPL", "price": 180.0}]

    # Исправленная проверка! Тест проверяет вызов ровно с одним аргументом (списком валют)
    mock_dependencies["currency"].assert_called_once_with(["USD", "EUR"])
    mock_dependencies["stock"].assert_called_once_with(["AAPL", "GOOGL"])


def test_generate_json_response_missing_date():
    """Тест сценария, когда передана пустая строка вместо даты."""
    response = generate_json_response("")
    assert response == {"error": "Параметр даты обязателен"}


def test_generate_json_response_invalid_date_format(mock_dependencies):
    """Тест сценария, когда get_month_range генерирует ValueError."""
    mock_dependencies["range"].side_effect = ValueError("Неверный формат даты")

    response = generate_json_response("invalid-date")
    assert response == {"error": "Неверный формат даты"}


def test_generate_json_response_settings_file_missing(mock_dependencies):
    """Тест сценария, когда файл настроек физически отсутствует."""
    mock_dependencies["exists"].return_value = False

    response = generate_json_response("10.2023")
    assert "Файл настроек не найден по пути" in response["error"]


def test_generate_json_response_corrupted_json(mock_dependencies):
    """Тест сценария, когда файл настроек поврежден (ошибка JSONDecodeError)."""
    mock_dependencies["json_load"].side_effect = json.JSONDecodeError(
        "Expecting value", "", 0
    )

    response = generate_json_response("10.2023")
    assert response == {"error": "Файл настроек поврежден (неверный JSON)"}


def test_generate_json_response_api_failure_fallback(mock_dependencies):
    """Тест устойчивости: если внешние API ломаются, возвращаются пустые списки."""
    mock_dependencies["currency"].side_effect = Exception("Сервис валют недоступен")
    mock_dependencies["stock"].side_effect = Exception("Сервис акций лежит")

    response = generate_json_response("10.2023")

    assert response["status"] == "success"
    assert response["currencies_exchange_rub"] == []
    assert response["stock_prices_usd"] == []


# --------------------------------------------------
# ----- 8. Веб страницы---доп.ГЛАВНАЯ---------------
# --------------------------------------------------

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd

# Импортируем функцию из вашего модуля (укажите правильный путь импорта)
from src.views import generate_main_page_json


class TestGenerateMainPageJson(unittest.TestCase):

    @patch("src.views.parse_incoming_datetime")
    def test_invalid_date_format(self, mock_parse):
        """Тест поведения функции при неверном формате даты (ValueError)."""
        # Настраиваем вызов исключения при парсинге
        mock_parse.side_effect = ValueError(
            "Неверный формат. Используйте YYYY-MM-DD HH:MM:SS"
        )

        result = generate_main_page_json("invalid-date")

        # Ожидаем возврат словаря с ошибкой без выполнения остальной логики
        self.assertEqual(
            result, {"error": "Неверный формат. Используйте YYYY-MM-DD HH:MM:SS"}
        )

    @patch("src.views.os.path.exists")
    @patch("src.views.load_user_settings")
    @patch("src.views.get_currency_rates")
    @patch("src.views.get_stock_prices")
    def test_excel_file_not_found(
        self, mock_stocks, mock_currencies, mock_load_settings, mock_exists
    ):
        """Тест работы функции, когда Excel файл с транзакциями отсутствует на диске."""
        mock_exists.return_value = False
        mock_load_settings.return_value = (["USD"], ["AAPL"])
        mock_currencies.return_value = [{"currency": "USD", "rate": 91.5}]
        mock_stocks.return_value = [{"currency": "AAPL", "rate": 180.0}]

        result = generate_main_page_json("2026-06-07 13:05:21")

        # Проверяем, что блоки карт и транзакций пустые, а внешние API подтянулись
        self.assertEqual(result["cards"], [])
        self.assertEqual(result["top_transactions"], [])
        self.assertEqual(result["currency_rates"], [{"currency": "USD", "rate": 91.5}])
        self.assertEqual(result["stock_prices"], [{"currency": "AAPL", "rate": 180.0}])

    @patch("src.views.os.path.exists")
    @patch("src.views.pd.read_excel")
    @patch("src.views.load_user_settings")
    @patch("src.views.get_currency_rates")
    @patch("src.views.get_stock_prices")
    def test_successful_generation(
        self,
        mock_stocks,
        mock_currencies,
        mock_load_settings,
        mock_read_excel,
        mock_exists,
    ):
        """Интеграционный тест успешной сборки JSON со всеми агрегациями Pandas и API."""
        mock_exists.return_value = True
        mock_load_settings.return_value = ([], [])
        mock_currencies.return_value = []
        mock_stocks.return_value = []

        # Создаем тестовый DataFrame, имитирующий содержимое Excel
        mock_df = pd.DataFrame(
            {
                "Дата операции": ["01.06.2026", "02.06.2026", "05.06.2026"],
                "Сумма платежа": [
                    -10000.0,
                    -5000.0,
                    15000.0,
                ],  # Два расхода, одно поступление
                "Номер карты": ["*4444", "*4444", "*1111"],
                "Категория": ["Супермаркеты", "Фастфуд", "Зарплата"],
                "Описание": ["Пятерочка", "Бургер Кинг", "Перевод"],
            }
        )
        mock_read_excel.return_value = mock_df

        # Запускаем генерацию для 7 июня (данные от 1, 2 и 5 июня попадают в маску)
        result = generate_main_page_json("2026-06-07 13:05:21")

        # 1. Проверяем расчет по картам (сумма расходов: 10000 + 5000 = 15000, кэшбэк = 150)
        self.assertEqual(len(result["cards"]), 1)
        self.assertEqual(result["cards"][0]["last_digits"], "4444")
        self.assertEqual(result["cards"][0]["total_spent"], 15000.0)
        self.assertEqual(result["cards"][0]["cashback"], 150.0)

        # 2. Проверяем топ транзакций (сортировка по модулю суммы, первыми идут 15000 и -10000)
        self.assertEqual(len(result["top_transactions"]), 3)
        self.assertEqual(result["top_transactions"][0]["amount"], 15000.0)
        self.assertEqual(result["top_transactions"][1]["amount"], -10000.0)
        self.assertEqual(result["top_transactions"][0]["category"], "Зарплата")

    @patch("src.views.os.path.exists")
    @patch("src.views.pd.read_excel")
    @patch("src.views.load_user_settings")
    @patch("src.views.get_currency_rates")
    @patch("src.views.get_stock_prices")
    def test_excel_processing_exception(
        self,
        mock_stocks,
        mock_currencies,
        mock_load_settings,
        mock_read_excel,
        mock_exists,
    ):
        """Тест устойчивости функции к критическим сбоям при обработке Excel (блок try-except)."""
        mock_exists.return_value = True
        # Имитируем поломку парсера или повреждение структуры Excel-файла
        mock_read_excel.side_effect = Exception("Системная ошибка чтения Excel")

        mock_load_settings.return_value = ([], [])
        mock_currencies.return_value = []
        mock_stocks.return_value = []

        # Функция не должна упасть; блоки Excel вернут пустые списки, но API отработает
        result = generate_main_page_json("2026-06-07 13:05:21")
        self.assertEqual(result["cards"], [])
        self.assertEqual(result["top_transactions"], [])
        self.assertIn("greeting", result)


if __name__ == "__main__":
    unittest.main()

# --------------------------------------------------
# ----- 14. main------------------------------------
# --------------------------------------------------

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.views import generate_main_page_data


@pytest.fixture
def mock_main_dependencies():
    """Фикстура для изоляции внешних вызовов функции generate_main_page_data."""
    with patch("src.views.parse_incoming_datetime") as mock_parse, patch(
        "src.views.get_greeting"
    ) as mock_greet, patch("src.views.os.path.exists") as mock_exists, patch(
        "src.views.pd.read_excel"
    ) as mock_read_excel, patch(
        "src.views.load_user_settings"
    ) as mock_load_settings, patch(
        "src.views.get_currency_rates"
    ) as mock_currency, patch(
        "src.views.get_stock_prices"
    ) as mock_stock:

        # Настройки по умолчанию
        mock_parse.return_value = (datetime(2026, 6, 1), datetime(2026, 6, 7))
        mock_greet.return_value = "Добрейший вечерочек"
        mock_exists.return_value = True
        mock_load_settings.return_value = (["USD"], ["AAPL"])
        mock_currency.return_value = [{"currency": "USD", "rate": 90.0}]
        mock_stock.return_value = [{"stock": "AAPL", "price": 180.0}]

        yield {
            "parse": mock_parse,
            "greet": mock_greet,
            "exists": mock_exists,
            "read_excel": mock_read_excel,
            "load_settings": mock_load_settings,
            "currency": mock_currency,
            "stock": mock_stock,
        }


def test_generate_main_page_data_success(mock_main_dependencies):
    """Тест успешного формирования агрегированных данных главной страницы."""
    # Имитируем таблицу транзакций Excel
    fake_excel_data = {
        "Дата операции": ["01.06.2026", "02.06.2026", "10.12.2025"],
        "Статус": ["OK", "OK", "OK"],
        "Номер карты": ["*4444", "*4444", "*1111"],
        "Сумма платежа": [-5000.0, -1500.0, -2000.0],
        "Сумма операции": [-5000.0, -1500.0, -2000.0],
        "Категория": ["Супермаркеты", "Одежда", "Фастфуд"],
        "Описание": ["Покупка еды", "Покупка куртки", "Мимо кассы"],
    }
    mock_main_dependencies["read_excel"].return_value = pd.DataFrame(fake_excel_data)

    response = generate_main_page_data("07.06.2026")

    # Проверяем базовые поля
    assert response["greeting"] == "Добрейший вечерочек"
    assert response["currency_rates"] == [{"currency": "USD", "rate": 90.0}]
    assert response["stock_prices"] == [{"stock": "AAPL", "price": 180.0}]

    # Проверяем расчет по картам (транзакция от 10.12 не должна попасть в диапазон июня)
    assert len(response["cards"]) == 1
    assert response["cards"][0]["last_digits"] == "4444"
    assert response["cards"][0]["total_spent"] == 6500.0  # 5000 + 1500
    assert response["cards"][0]["cashback"] == 65.0  # 6500 / 100

    # Проверяем ТОП транзакции (в июне их всего 2 штуки)
    assert len(response["top_transactions"]) == 2
    assert response["top_transactions"][0]["amount"] == -5000.0


def test_generate_main_page_data_invalid_date(mock_main_dependencies):
    """Проверка обработки некорректного формата переданной даты."""
    mock_main_dependencies["parse"].side_effect = ValueError("Неверный формат даты")
    response = generate_main_page_data("bad-date")
    assert "error" in response
