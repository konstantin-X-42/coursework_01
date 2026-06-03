from pathlib import Path

# -------------------------------------------------------------------
# --- ИМПОРТЫ ФУНКЦИЙ ---
from src.decorators import log
from src.excel_csv_reader import transactions_csv, transactions_excel
from src.generators import filter_by_currency
from src.processing import filter_by_state, process_bank_operations, process_bank_search, sort_by_date
from src.utils import get_transactions
from src.widget import get_date, mask_account_card

# -------------------------------------------------------------------

# абсолютный путь к файлу лога относительно текущего файла main.py
LOG_FILE_PATH = Path(__file__).resolve().parent / "logs" / "main.log"


@log(str(LOG_FILE_PATH))  # type: ignore
def main():  # type: ignore
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    # Определяем корень проекта (на уровень выше, чем папка src, где лежит main.py)
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Формируем точные пути к файлам в папке data
    json_path = BASE_DIR / "data" / "operations.json"
    csv_path = BASE_DIR / "data" / "transactions.csv"
    xlsx_path = BASE_DIR / "data" / "transactions_excel.xlsx"

    # --------------------------------
    # # Пути к файлам данных
    # data_dir = "data"
    # json_path = os.path.join(data_dir, "operations.json")
    # csv_path = os.path.join(data_dir, "transactions.csv")
    # xlsx_path = os.path.join(data_dir, "transactions_excel.xlsx")
    # --------------------------------

    # Переменная для хранения списка транзакций
    transactions = []

    # 1. Выбор источника данных
    while True:
        choice = input("\nПользователь: ").strip()
        if choice == "1":
            print("\nПрограмма: Для обработки выбран JSON-файл.")
            transactions = get_transactions(json_path)
            break
        elif choice == "2":
            print("\nПрограмма: Для обработки выбран CSV-файл.")
            transactions = transactions_csv(str(csv_path))
            break
        elif choice == "3":
            print("\nПрограмма: Для обработки выбран XLSX-файл.")
            transactions = transactions_excel(str(xlsx_path))
            break
        else:
            print("Программа: Неверный пункт меню. Пожалуйста, выберите 1, 2 или 3.")

    # 2. Фильтрация по статусу
    valid_statuses = ["EXECUTED", "CANCELED", "PENDING"]
    while True:
        print("\nПрограмма: Введите статус, по которому необходимо выполнить фильтрацию.")
        print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")

        status_input = input("\nПользователь: ").strip().upper()

        if status_input in valid_statuses:
            print(f'\nПрограмма: Операции отфильтрованы по статусу "{status_input}"')
            # СТЫКОВКА: Фильтруем по статусу state
            transactions = filter_by_state(transactions, status_input)
            break
        else:
            print(f'\nПрограмма: Статус операции "{status_input}" недоступен.')

    # 3. Сортировка по дате
    print("\nПрограмма: Отсортировать операции по дате? Да/Нет")
    sort_choice = input("\nПользователь: ").strip().lower()

    if sort_choice == "да":
        print("\nПрограмма: Отсортировать по возрастанию или по убыванию?")
        order_choice = input("\nПользователь: ").strip().lower()

        ascending = True if "возраст" in order_choice else False
        # СТЫКОВКА: Сортируем с помощью sort_by_date
        transactions = sort_by_date(transactions, reverse=not ascending)

    # 4. Фильтрация по валюте (только рубли)
    print("\nПрограмма: Выводить только рублевые транзакции? Да/Нет")
    rub_choice = input("\nПользователь: ").strip().lower()

    if rub_choice == "да":
        transactions = list(filter_by_currency(transactions, "RUB"))

    # 5. Фильтрация по ключевому слову в описании
    print("\nПрограмма: Отфильтровать список транзакций по определенному слову в описании? Да/Нет")
    desc_choice = input("\nПользователь: ").strip().lower()

    if desc_choice == "да":
        search_word = input("\nПрограмма: Введите слово для поиска:\nПользователь: ").strip()
        # СТЫКОВКА: Вызываем регистронезависимый поиск
        transactions = process_bank_search(transactions, search_word)

    # 6. Вывод результатов
    print("\nПрограмма: Распечатываю итоговый список транзакций...")

    if not transactions:
        print("\nПрограмма: Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
    else:
        print(f"\nПрограмма:\nВсего банковских операций в выборке: {len(transactions)}\n")

        # СТЫКОВКА С КАТЕГОРИЯМИ: Показываем сводку по часто встречающимся операциям
        test_categories = ["Перевод организации", "Интернет-банк", "Оплата"]
        stats = process_bank_operations(transactions, test_categories)

        print("Статистика по ключевым категориям:")
        for category, count in stats.items():
            print(f" - {category}: {count} шт.")
        print("-" * 40)

        # Вывод списка транзакций через маскирование
        for tx in transactions:
            # Получаем дату и маскируем её через widget
            raw_date = tx.get("date", "")
            formatted_date = get_date(raw_date) if raw_date else "00.00.0000"

            # Описание операции
            description = tx.get("description", "Без описания")

            # Маскируем карту или счет отправителя/получателя
            from_info = tx.get("from", "")
            to_info = tx.get("to", "")

            masked_from = mask_account_card(from_info) if from_info else "Новый счет"
            masked_to = mask_account_card(to_info) if to_info else "Не указан"

            # Расчет суммы в рублях (если валюта не RUB, можно применить conversion_rub)
            amount = tx.get("operationAmount", {}).get("amount", "0")
            currency = tx.get("operationAmount", {}).get("currency", {}).get("name", "")

            print(f"{formatted_date} {description}")
            print(f"{masked_from} -> {masked_to}")
            print(f"Сумма: {amount} {currency}\n")


if __name__ == "__main__":
    main()
