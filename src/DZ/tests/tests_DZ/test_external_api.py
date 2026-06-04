import unittest
from unittest.mock import MagicMock, patch  # импортируем patch — функция-декоратор и MagicMock — создания заглушек

import requests

from src.DZ.external_api import conversion_rub  # Импортируем тестируемую функцию

"""
показать подробный отчет (название каждого теста и статус).
pytest tests/test_external_api.py -v
python -m unittest tests/test_external_api.py -v

выводить print() в консоль во время работы тестов.
pytest tests/test_external_api.py -s
"""


class TestExternalApi(unittest.TestCase):

    @patch("src.external_api.requests.get")
    def test_conversion_rub_success(self, mock_get: MagicMock) -> None:
        """Проверяем конвертацию валюты USD через API"""
        # Настраиваем mock-ответ от API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 7500.0}
        mock_get.return_value = mock_response

        # Подменяем API_KEY
        with patch("src.external_api.API_KEY", "test_secret_key"):
            result = conversion_rub(100.0, "USD")

        self.assertEqual(result, 7500.0)
        # Проверяем параметры отправленного запроса
        mock_get.assert_called_once_with(
            "https://api.apilayer.com/exchangerates_data/convert",
            headers={"apikey": "test_secret_key"},
            params={"to": "RUB", "from": "USD", "amount": 100.0},
        )

    @patch("src.external_api.requests.get")
    def test_conversion_rub_already_rub(self, mock_get: MagicMock) -> None:
        """Проверяем, если валюта RUB, API не должно вызываться"""
        result = conversion_rub(150.0, "RUB")

        self.assertEqual(result, 150.0)
        # Убеждаемся, что сетевой запрос не выполнялся
        mock_get.assert_not_called()

    def test_conversion_rub_missing_api_key(self) -> None:
        """Проверяем при отсутствии API-ключа функция возвращает 0.0"""
        with patch("src.external_api.API_KEY", None):
            result = conversion_rub(100.0, "EUR")

        self.assertEqual(result, 0.0)

    @patch("src.external_api.requests.get")
    def test_conversion_rub_http_error(self, mock_get: MagicMock) -> None:
        """Проверяем обработку сетевых ошибок (например, 404 или HTTPError)"""
        mock_response = MagicMock()
        # Имитируем вызов исключения при raise_for_status()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")
        mock_get.return_value = mock_response

        with patch("src.external_api.API_KEY", "test_key"):
            result = conversion_rub(100.0, "EUR")

        self.assertEqual(result, 0.0)

    @patch("src.external_api.requests.get")
    def test_conversion_rub_invalid_json(self, mock_get: MagicMock) -> None:
        """Проверяем обработку некорректного ответа (отсутствует ключ 'result')"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Имитируем ответ без нужного ключа
        mock_response.json.return_value = {"status": "success"}
        mock_get.return_value = mock_response

        with patch("src.external_api.API_KEY", "test_key"):
            result = conversion_rub(100.0, "USD")

        # Так как .get("result", 0.0) вернет 0.0, функция должна вернуть 0.0
        self.assertEqual(result, 0.0)


if __name__ == "__main__":
    unittest.main()
