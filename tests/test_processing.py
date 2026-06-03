import pytest

from src.processing import filter_by_state, process_bank_operations, process_bank_search, sort_by_date


def test_correct_get_date_executed(date_list_executed):
    assert (
        filter_by_state(
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ]
        )
        == date_list_executed
    )


def test_correct_get_date_canceled(date_list_canceled):
    assert (
        filter_by_state(
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ],
            "CANCELED",
        )
        == date_list_canceled
    )


def test_not_correct_get_date_executed(date_list_executed):
    assert (
        filter_by_state(
            [
                {"id": 41428829, "state": "EXECUTE", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ]
        )
        != date_list_executed
    )
    assert (
        filter_by_state(
            [
                {"id": 41428829, "stat": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ]
        )
        != date_list_executed
    )
    assert filter_by_state() != date_list_executed


# --------------------------------------------------------------------
# --------------------------------------------------------------------


def test_correct_sort_by_date_true(date_list_true):
    assert (
        sort_by_date(
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ]
        )
        == date_list_true
    )


def test_correct_sort_by_date_false(date_list_false):
    assert (
        sort_by_date(
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ],
            False,
        )
        == date_list_false
    )


def test_not_correct_sort_by_date_true(date_list_true):
    assert (
        sort_by_date(
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "dat": "2018-06-30T02:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ]
        )
        != date_list_true
    )
    assert (
        sort_by_date(
            [
                {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
                {"id": 939719570, "state": "EXECUTED", "date": "201фига2:08:58.425572"},
                {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
                {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
            ]
        )
        != date_list_true
    )
    assert sort_by_date() != date_list_true


def test_sort_by_date_none():
    # Проверяем, что функция возвращает список с ошибкой, если передать None
    assert sort_by_date(None) == []  # "Error_13 - в функцию не подаются аргументы"


# --------------------------------------------------------------------
#                process_bank_search(data, search)
# --------------------------------------------------------------------


@pytest.fixture
def sample_data():
    """Фикстура с тестовыми данными банковских операций."""
    return [
        {"id": 1, "description": "Перевод организации"},
        {"id": 2, "description": "Оплата услуг: Мобильная связь"},
        {"id": 3, "description": "Перевод частному лицу"},
        {"id": 4, "description": None},
        {"id": 5, "amount": 100},  # Отсутствует ключ description
        "не валидный словарь",  # Некорректный тип данных в списке
    ]


def test_search_empty_query(sample_data):
    """Проверяем пустая строка поиска возвращает исходные данные без изменений"""
    assert process_bank_search(sample_data, "") == sample_data
    assert process_bank_search(sample_data, None) == sample_data  # type: ignore


def test_search_case_insensitive(sample_data):
    """Проверяем поиск работает без учета регистра (больших и маленьких букв)"""
    expected = [{"id": 1, "description": "Перевод организации"}, {"id": 3, "description": "Перевод частному лицу"}]
    assert process_bank_search(sample_data, "пЕрЕвОд") == expected


def test_search_no_matches(sample_data):
    """Проверяем если совпадений нет, возвращается пустой список"""
    assert process_bank_search(sample_data, "Покупка продуктов") == []


def test_search_substring(sample_data):
    """Проверяем поиск по части слова"""
    expected = [{"id": 2, "description": "Оплата услуг: Мобильная связь"}]
    assert process_bank_search(sample_data, "связь") == expected


def test_search_with_special_characters():
    """Проверяем корректную обработку специальных символов"""
    data = [{"id": 1, "description": "ООО 'Витязь'*"}, {"id": 2, "description": "Обычное описание"}]
    expected = [{"id": 1, "description": "ООО 'Витязь'*"}]
    assert process_bank_search(data, "*") == expected


def test_invalid_elements_ignored(sample_data):
    """Проверяем функцию на игнорирование элементов, которые не являются словарями или строками"""
    # "не валидный словарь" должен быть проигнорирован
    # элементы с description=None или без него не должны вызывать ошибку
    result = process_bank_search(sample_data, "Перевод")
    assert len(result) == 2
    for item in result:
        assert "Перевод" in item["description"]


# --------------------------------------------------------------------
#                process_bank_operations(data, categories)
# --------------------------------------------------------------------


@pytest.fixture
def sample_operations():
    """Фикстура с тестовым списком банковских операций"""
    return [
        {"id": 1, "description": "Перевод организации"},
        {"id": 2, "description": "Оплата мобильной связи"},
        {"id": 3, "description": "Перевод организации"},
        {"id": 4, "description": "Покупка продуктов"},
        {"id": 5, "description": "Оплата мобильной связи"},
        {"id": 6, "description": "Перевод организации"},
        {"id": 7, "description": None},  # Операция с пустым описанием
        {},  # Пустой словарь операции
    ]


def test_successful_counting(sample_operations):
    """Проверяем корректный подсчет существующих категорий"""
    categories = ["Перевод организации", "Оплата мобильной связи"]
    expected = {"Перевод организации": 3, "Оплата мобильной связи": 2}
    assert process_bank_operations(sample_operations, categories) == expected


def test_empty_categories(sample_operations):
    """Проверяем пустой список категорий возвращает пустой словарь"""
    assert process_bank_operations(sample_operations, []) == {}


def test_empty_operations_data():
    """Проверяем пустой список операций возвращает нули для всех категорий"""
    categories = ["Покупка продуктов", "Перевод организации"]
    expected = {"Покупка продуктов": 0, "Перевод организации": 0}
    assert process_bank_operations([], categories) == expected


def test_category_not_in_data(sample_operations):
    """Проверяем категория, которой нет в данных, возвращает 0"""
    categories = ["Снятие наличных"]
    expected = {"Снятие наличных": 0}
    assert process_bank_operations(sample_operations, categories) == expected


def test_mixed_results(sample_operations):
    """Проверяем запрос существующих и отсутствующих категорий одновременно"""
    categories = ["Покупка продуктов", "Неизвестная категория"]
    expected = {"Покупка продуктов": 1, "Неизвестная категория": 0}
    assert process_bank_operations(sample_operations, categories) == expected
