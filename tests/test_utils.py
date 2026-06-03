from unittest.mock import mock_open, patch  # импортируем декоратор патч и модуль мок

from src.utils import get_transactions  # путь к модулю

"""
показать подробный отчет (название каждого теста и статус).
pytest tests/test_utils.py -v

выводить print() в консоль во время работы тестов.
pytest tests/test_utils.py -s
"""


@patch("src.utils.Path.is_file")
def test_get_transactions_success(mock_is_file):
    """Проверяем JSON-файл на корректность чтения, функция возвращает список - массив словарей"""
    mock_is_file.return_value = True
    mock_data = '[{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]'

    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = get_transactions("valid.json")

    assert result == [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]


@patch("src.utils.Path.is_file")
def test_get_transactions_file_not_found(mock_is_file):
    """Проверяем существование файла по указанному пути и то, что этот файл не папка"""
    mock_is_file.return_value = False

    result = get_transactions("fake_path.json")

    assert result == []


@patch("src.utils.Path.is_file")
def test_get_transactions_not_a_list(mock_is_file):
    """Проверяем JSON-файл корректен, но корневой элемент — словарь, а не список, функция возвращает пустой []"""
    mock_is_file.return_value = True
    mock_data = '{"status": "error", "message": "not a list"}'

    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = get_transactions("dict.json")

    assert result == []


@patch("src.utils.Path.is_file")
def test_get_transactions_invalid_json(mock_is_file):
    """Проверяем если JSON-файл повреждён (JSONDecodeError), функция возвращает пустой []"""
    mock_is_file.return_value = True
    mock_data = '[{"id": 1, "amount": 100'  # Пропущена закрывающая скобка

    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = get_transactions("corrupted.json")

    assert result == []


@patch("src.utils.Path.is_file")
def test_get_transactions_empty_file(mock_is_file):
    """Проверяем JSON-файл пустой, функция возвращает пустой []"""
    mock_is_file.return_value = True

    with patch("builtins.open", mock_open(read_data="")):
        result = get_transactions("empty.json")

    assert result == []
