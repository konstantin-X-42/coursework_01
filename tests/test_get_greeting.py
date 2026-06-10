# --------------------------------------------------
# ----- 6. Веб страницы---доп.ГЛАВНАЯ---------------
# --------------------------------------------------
# запуск тестов
# pytest tests/test_get_greeting.py
# --------------------------------------------------

# ==========================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ    get_greeting()
# ==========================================

import unittest
from datetime import datetime
from unittest.mock import patch

# Импортируем тестируемую функцию
from src.utils import get_greeting


class TestGetGreeting(unittest.TestCase):

    @patch("src.utils.datetime")
    def test_get_greeting_morning(self, mock_datetime_module):
        """Проверка утреннего интервала (06:00 - 11:59)."""
        # Настраиваем mock так, чтобы datetime.now() возвращал нужное время,
        # но при этом сам класс datetime оставался доступен для isinstance
        mock_datetime_module.now.return_value = datetime(2026, 6, 10, 9, 0, 0)
        mock_datetime_module.datetime = datetime

        self.assertEqual(get_greeting(datetime.now()), "Доброе утро")

    @patch("src.utils.datetime")
    def test_get_greeting_afternoon(self, mock_datetime_module):
        """Проверка дневного интервала (12:00 - 17:59)."""
        mock_datetime_module.now.return_value = datetime(2026, 6, 10, 15, 0, 0)
        mock_datetime_module.datetime = datetime

        self.assertEqual(get_greeting(datetime.now()), "Добрый день")

    @patch("src.utils.datetime")
    def test_get_greeting_evening(self, mock_datetime_module):
        """Проверка вечернего интервала (18:00 - 22:59)."""
        mock_datetime_module.now.return_value = datetime(2026, 6, 10, 20, 0, 0)
        mock_datetime_module.datetime = datetime

        self.assertEqual(get_greeting(datetime.now()), "Добрый вечер")

    @patch("src.utils.datetime")
    def test_get_greeting_night(self, mock_datetime_module):
        """Проверка ночного интервала (23:00 - 05:59)."""
        mock_datetime_module.now.return_value = datetime(2026, 6, 10, 3, 0, 0)
        mock_datetime_module.datetime = datetime

        self.assertEqual(get_greeting(datetime.now()), "Доброй ночи")


if __name__ == "__main__":
    unittest.main()
