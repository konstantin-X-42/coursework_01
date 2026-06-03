#  --  --  --  --  --  --  --  --  --  --  --  --  --
"""
Команда запуск теста ошибки в консоль
pytest -s tests/test_excel_csv_reader.py

Команда запуск теста
poetry run pytest tests/test_excel_csv_reader.py
"""

#  --  --  --  --  --  --  --  --  --  --  --  --  --

import unittest
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.excel_csv_reader import transactions_csv, transactions_excel


@patch("csv.DictReader")
def test_transactions_csv_success(mock_dict_reader):
    """Проверяем успешное чтение данных из CSV с использованием mock"""

    # Имитируем данные, которые должен вернуть csv.DictReader
    mock_rows = [
        {
            "id": "650703",
            "state": "EXECUTED",
            "amount": "1500.50",
            "currency": "RUB",
        },
        {
            "id": "123456",
            "state": "PENDING",
            "amount": "100.00",
            "currency": "USD",
        },
    ]

    # Настраиваем mock, при итерации по DictReader он должен возвращать словари
    mock_dict_reader.return_value = mock_rows

    # Мокаем встроенную функцию open, чтобы Python не искал файл на диске
    # mock_open() создает имитацию файла
    with patch("builtins.open", mock_open(read_data="")):
        # Вызываем функцию с любым вымышленным путем
        result = transactions_csv("path.csv")

    # Проверяем результаты (assert)
    assert len(result) == 2
    assert result[0]["id"] == "650703"
    assert result[1]["currency"] == "USD"
    # Проверяем, что элементы внутри — это обычные словари
    assert isinstance(result[0], dict)


@patch("builtins.open", side_effect=FileNotFoundError)
def test_transactions_csv_no_file(mock_builtin_open):
    """Проверяем исключение, если файл не найден"""

    # Проверяем, что функция прокидывает ошибку FileNotFoundError наружу
    with pytest.raises(FileNotFoundError):
        transactions_csv("error.csv")


#  --  --  --  --  --  --  --  --  --  --  --  --  --
#  --  --  --  --  --  --  --  --  --  --  --  --  --


class TestTransactionsExcel(unittest.TestCase):

    @patch("os.path.exists")
    @patch("pandas.read_excel")
    def test_transactions_xlsx_success(self, mock_read_excel, mock_exists):
        """Проверяем успешное считывание и очистку данных"""
        # Настраиваем mock, файл якобы существует
        mock_exists.return_value = True

        # Создаем тестовый DataFrame с данными и пробелами в колонках, NaN
        mock_df = pd.DataFrame({"  Дата  ": ["2026-05-29", "2026-05-30"], "Сумма": ["1500", None]})
        mock_read_excel.return_value = mock_df

        # Вызываем тестируемую функцию
        result = transactions_excel("dummy_path.xlsx")

        # Проверяем, что read_excel вызывался с правильными параметрами
        mock_read_excel.assert_called_once_with("dummy_path.xlsx", dtype=str)

        # Проверяем корректность очистки и трансформации
        expected = [{"Дата": "2026-05-29", "Сумма": "1500"}, {"Дата": "2026-05-30", "Сумма": ""}]
        self.assertEqual(result, expected)

    @patch("os.path.exists")
    def test_transactions_xlsx_no_file(self, mock_exists):
        """Проверяем исключение, если файл не найден"""
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            transactions_excel("error.xlsx")

    @patch("os.path.exists")
    @patch("pandas.read_excel")
    def test_pandas_exception(self, mock_read_excel, mock_exists):
        """Проверяем ошибку при чтении файла внутри pandas"""
        mock_exists.return_value = True
        # Имитируем поломку парсера Excel, файл поврежден
        mock_read_excel.side_effect = Exception("Разрушен формат файла")

        with self.assertRaises(RuntimeError) as context:
            transactions_excel("error.xlsx")

        self.assertIn("Ошибка при чтении Excel-файла", str(context.exception))


if __name__ == "__main__":
    unittest.main()
