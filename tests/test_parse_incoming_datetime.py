import unittest
from datetime import datetime
from unittest.mock import patch

from src.utils import parse_incoming_datetime

# ==========================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ    parse_incoming_datetime()
# ==========================================
# --------------------------------------------------
# запуск тестов
# pytest tests/test_parse_incoming_datetime.py
# --------------------------------------------------


class TestParseIncomingDatetime(unittest.TestCase):

    # ИСПРАВЛЕНО: патчим логер именно в src.utils
    @patch("src.utils.logger")
    def test_parse_success(self, mock_logger):
        """Тест успешного парсинга корректной строки."""
        input_str = "2026-06-07 13:05:21"
        start_date, end_date = parse_incoming_datetime(input_str)

        self.assertEqual(end_date, datetime(2026, 6, 7, 13, 5, 21))
        self.assertEqual(start_date, datetime(2026, 6, 1, 0, 0, 0))

    # ИСПРАВЛЕНО: патчим логер именно в src.utils
    @patch("src.utils.logger")
    def test_parse_invalid_format(self, mock_logger):
        """Тест генерации ValueError при неверном формате строки."""
        invalid_inputs = [
            "2026-06-07",
            "07-06-2026 13:05:21",
            "2026/06/07 13:05:21",
            "not-a-date-string",
        ]

        for bad_input in invalid_inputs:
            with self.subTest(bad_input=bad_input):
                with self.assertRaises(ValueError) as context:
                    parse_incoming_datetime(bad_input)

                self.assertEqual(
                    str(context.exception),
                    "Неверный формат. Используйте YYYY-MM-DD HH:MM:SS",
                )

                # Теперь проверка сработает корректно
                self.assertTrue(
                    mock_logger.error.called, f"Логер не был вызван для: {bad_input}"
                )


if __name__ == "__main__":
    unittest.main()
