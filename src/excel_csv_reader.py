import csv
import os
from typing import Any, Dict, List, cast

import pandas as pd


def transactions_csv(file_path: str) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из CSV-файла.

    :param file_path: Путь к файлу CSV с данными транзакций.
    :return: Список словарей, где каждый словарь — это одна операция.
    """
    transactions = []

    # utf-8-sig автоматически удаляет невидимый маркер BOM, который часто создает Excel
    with open(file_path, mode="r", encoding="utf-8-sig") as file:
        # DictReader автоматически использует первую строку файла как ключи словаря
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            # Превращаем row (объект DictRow) в обычный словарь Python
            transactions.append(dict(row))

    return transactions


#  --  --  --  --  --  --  --  --  --  --  --  --  --

# --- БЛОК ИНИЦИАЛИЗАЦИИ ФУНКЦИИ ---
if __name__ == "__main__":

    # Автоматически определяем путь к папке со скриптом
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Собираем абсолютный путь к файлу внутри папки: data_13_2_10
    # Модуль excel_csv_reader.py лежит в src/, папка data_13_2_10 в корне проекта, поднимаемся на один уровень вверх:
    path = os.path.abspath(os.path.join(current_dir, "..", "data_13_2_10", "transactions.csv"))

    # print(transactions_csv(path))

# --------------------------------------------------------------------


def transactions_excel(file_path: str) -> List[Dict[str, Any]]:
    """Считывает финансовые операции из Excel-файла.

    :param file_path: Путь к файлу Excel с данными транзакций.
    :return: Список словарей, где каждый словарь — это одна операция.
    """
    # Проверяем существование файла
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл по пути {file_path} не найден.")

    try:
        # Читаем Excel (автоматически пропускает пустые строки в конце)
        df = pd.read_excel(file_path, dtype=str)

        # Очищаем данные: заменяем NaN на пустые строки, убираем пробелы в названиях колонок
        df = df.fillna("")
        df.columns = df.columns.str.strip()

        # Преобразуем DataFrame в список словарей
        transactions = df.to_dict(orient="records")

        return cast(List[Dict[str, Any]], transactions)

    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении Excel-файла: {e}")


#  --  --  --  --  --  --  --  --  --  --  --  --  --

# --- БЛОК ИНИЦИАЛИЗАЦИИ ФУНКЦИИ ---
if __name__ == "__main__":

    # Автоматически определяем путь к папке со скриптом
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Собираем абсолютный путь к файлу внутри папки: data_13_2_10
    # Модуль excel_csv_reader.py лежит в src/, папка data_13_2_10 в корне проекта, поднимаемся на один уровень вверх:
    path = os.path.abspath(os.path.join(current_dir, "..", "data_13_2_10", "transactions_excel.xlsx"))

    print(transactions_excel(path))
