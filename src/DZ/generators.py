from typing import Any, Iterator

# блок входных данных передаём в аргумент функции
transactions_data = [
    {
        "id": 939719570,
        "state": "EXECUTED",
        "date": "2018-06-30T02:08:58.425572",
        "operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
        "description": "Перевод организации",
        "from": "Счет 75106830613657916952",
        "to": "Счет 11776614605963066702",
    },
    {
        "id": 142264268,
        "state": "EXECUTED",
        "date": "2019-04-04T23:20:05.206878",
        "operationAmount": {"amount": "79114.93", "currency": {"name": "USD", "code": "USD"}},
        "description": "Перевод со счета на счет",
        "from": "Счет 19708645243227258542",
        "to": "Счет 75651667383060284188",
    },
    {
        "id": 873106923,
        "state": "EXECUTED",
        "date": "2019-03-23T01:09:46.296404",
        "operationAmount": {"amount": "43318.34", "currency": {"name": "руб.", "code": "RUB"}},
        "description": "Перевод со счета на счет",
        "from": "Счет 44812258784861134719",
        "to": "Счет 74489636417521191160",
    },
    {
        "id": 895315941,
        "state": "EXECUTED",
        "date": "2018-08-19T04:27:37.904916",
        "operationAmount": {"amount": "56883.54", "currency": {"name": "USD", "code": "USD"}},
        "description": "Перевод с карты на карту",
        "from": "Visa Classic 6831982476737658",
        "to": "Visa Platinum 8990922113665229",
    },
    {
        "id": 594226727,
        "state": "CANCELED",
        "date": "2018-09-12T21:27:25.241689",
        "operationAmount": {"amount": "67314.70", "currency": {"name": "руб.", "code": "RUB"}},
        "description": "Перевод организации",
        "from": "Visa Platinum 1246377376343588",
        "to": "Счет 14211924144426031657",
    },
]

# --------------------------------------------------------------------


# функция-генератор
def filter_by_currency(transactions: list[dict[str, Any]], currency: str) -> Iterator[dict[str, Any]]:
    """
    Генератор, фильтрует транзакции по заданной валюте, выгружает пакетами элементов списка в (dict)
    """
    for transaction in transactions:
        # Проверяем, что transaction — это словарь, и только тогда ищем валюту
        if (
            isinstance(transaction, dict)
            and transaction.get("operationAmount", {}).get("currency", {}).get("code") == currency
        ):
            yield transaction


# вызов функции в теле модуля (при условии, что функция не импортирована из другого модуля)
# if __name__ == "__main__":
#     print("--- ТЕСТ filter_by_currency() ---")
#     usd_transactions = filter_by_currency(transactions_data, "RUB")  # создаем генератор ОДИН РАЗ
#     # Выводим результаты по очереди
#     for _ in range(3):
#         try:
#             print(next(usd_transactions))
#         except StopIteration:
#             print("Транзакции в этой валюте закончились.")


# --------------------------------------------------------------------


def transaction_descriptions(transactions: list[dict[str, Any]]) -> Iterator[str]:
    """
    Принимает список словарей и возвращает описание (description) каждой транзакции.
    """
    for transaction in transactions:
        # если ключа нет, возвращает вместо пустой строки "Описание отсутствует"
        yield transaction.get("description", "Описание отсутствует")


descriptions = transaction_descriptions(transactions_data)

# if __name__ == "__main__":
#     print("--- ТЕСТ transaction_descriptions() ---")
#     for desc in descriptions:
#         print(f"Описание: {desc}")


# --------------------------------------------------------------------


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """
    Генерирует номера карт в формате XXXX XXXX XXXX XXXX в заданном диапазоне.
    """
    for number in range(start, end + 1):
        card_str = f"{number:016}"  # делает строку длиной 16 символов,
        # если в аргументе число короче — допишет в начало нули (:016)

        # разбивает строку на блоки по 4 цифры и соединяет их пробелами
        formatted_card = f"{card_str[:4]} {card_str[4:8]} {card_str[8:12]} {card_str[12:]}"

        yield formatted_card


# if __name__ == "__main__":
#     print("--- ТЕСТ card_number_generator() ---")
#     for card_number in card_number_generator(1, 5):
#         print(card_number)
