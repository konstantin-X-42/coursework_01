import re
from collections import Counter
from typing import Any


def filter_by_state(
    date_list: list[dict[str, Any]] | tuple[dict[str, Any]] | None = None, state: str = "EXECUTED"
) -> Any:  # list[dict[str, Any]]:
    """функция возвращает массив с выбранным ключом state по умолчанию возвращает с 'EXECUTED'"""

    try:  # обработка исключений
        if date_list is None:
            return []  # "Error_11 - в функцию не подаются аргументы"
        state_list = []

        for state_dict in date_list:  # итерируем словари из списка (массива)
            if isinstance(state_dict, dict):
                # Безопасно достаем статус и убираем лишние пробелы, если это строка
                current_state = state_dict.get("state")
                if isinstance(current_state, str) and current_state.strip() == state:
                    state_list.append(state_dict)  # добавляем словарь в конец списка каждую итерацию
        return state_list
    except KeyError:  # обращение к элементу словаря (dict) по key, которого в этом словаре нет
        return []  # "Error_12 - в аргументе функции, key в словарях или в одном из словарей отсутствует"
    # except Exception:  # другая непредвиденная ошибка
    #     return []  # "Error_11 - в функцию не подаются аргументы или поданы в ином формате"


# --------------------------------------------------------------------


def sort_by_date(date_list: list[dict[str, Any]] | None = None, reverse: bool = True) -> Any:  # list[dict[str, Any]]:
    """функция сортирует словари по дате: на убывание - по умолчанию или на возрастание,
    по установленному значению в аргументе - sorting"""

    try:  # обработка исключений
        if date_list is None:
            return []  # "Error_13 - в функцию не подаются аргументы"

        return sorted(
            date_list,
            key=lambda x: x.get("date", "") if isinstance(x, dict) else "",
            reverse=reverse,
        )
    except KeyError, TypeError:  # обращение к элементу словаря (dict) по key, которого в этом словаре нет
        return []  # "Error_14 - в аргументе функции, key в словарях или в одном из словарей отсутствует"


# --------------------------------------------------------------------
# --------------------------------------------------------------------


def process_bank_search(data: list[dict], search: str) -> list[dict]:  # type: ignore
    """функция фильтрует список банковских операций по строке поиска, без учета больших и маленьких букв"""
    if not search:
        return data

    pattern = re.compile(re.escape(search), re.IGNORECASE)
    result = []
    for operation in data:
        if not isinstance(operation, dict):
            continue
        description = operation.get("description")
        if isinstance(description, str):
            if pattern.search(description):
                result.append(operation)
    return result


# --------------------------------------------------------------------
# # --- ТЕСТОВЫЕ ДАННЫЕ ДЛЯ ЗАПУСКА ---
#
# Создаем список банковских операций
# operations_list = [
#     {"id": 1, "amount": 500, "description": "Перевод перевод другу"},
#     {"id": 2, "amount": 1200, "description": "Оплата супермаркета Пятерочка"},
#     {"id": 3, "amount": 150, "description": "Покупка кофе в кофемашине"},
#     {"id": 4, "amount": 3000, "description": "Оплата ЖКХ"},
# ]
#
# Задаем поисковый запрос
# search_query = "ОПЛАТА"
#
# Вызываем функцию и сохраняем результат
# filtered_operations = process_bank_search(operations_list, search_query)
#
# Выводим результат
# print(filtered_operations)


# --------------------------------------------------------------------
# --------------------------------------------------------------------


def process_bank_operations(data: list[dict], categories: list[str]) -> dict[str, int]:  # type: ignore
    """
    Подсчитывает количество банковских операций для каждой заданной категории на основе поля 'description',
    возвращает словарь, ключи — названия категорий, значения — количество.
    """
    if not categories:
        return {}

    # собираем все описания операций, пропуская пустые элементы
    descriptions = []
    for operation in data:
        if operation:
            desc = operation.get("description")
            descriptions.append(desc)

    # подсчитываем количество упоминаний
    counts = Counter(descriptions)

    # словарь с запрошенными категорий
    res = {}
    for category in categories:
        res[category] = counts[category]  # количество повторений в словарь
    return res


# --------------------------------------------------------------------

# --- ТЕСТОВЫЕ ДАННЫЕ ---
# mock_data = [
#     {"amount": 100, "description": "Супермаркет"},
#     {"amount": 200, "description": "Супермаркет"},
#     {"amount": 50, "description": "Автозаправка"},
#     {"amount": 300, "description": "Ресторан"},
#     {"amount": 15, "description": None},  # проверка на None
#     {},  # проверка на пустой словарь
# ]
#
# test_categories = ["Супермаркет", "Автозаправка", "Кино"]
#
# --- ЗАПУСК ---
# result = process_bank_operations(mock_data, test_categories)
# print(result)
# Ожидаемый вывод: {'Супермаркет': 2, 'Автозаправка': 1, 'Кино': 0}
