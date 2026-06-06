#--------------------------------------------------
#----- 2. Веб страницы---ОСНОВНАЯ------------------
#--------------------------------------------------
# установка библиотеки uvicorn - выполняет роль веб-сервера
# poetry add uvicorn

# установка библиотеки FastAPI - фреймворк для создания HTTP API на Python
# poetry add fastapi

# запуск сервера
# poetry run uvicorn src.main:app --reload
# остановка сервера
# ctrl + c

# запрос в браузер
# http://127.0.0.1:8000/docs
# нажать Try it out >>> ввести дату, имеющуюся в operations.xlsx


from fastapi import FastAPI, HTTPException
from src.views import analytics_view

app = FastAPI()

@app.get("/analytics")
def get_analytics(date: str = None):
    result = analytics_view(date)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
#--------------------------------------------------
#----- 3. Веб страницы---ОСНОВНАЯ--API-------------
#--------------------------------------------------
from src.views import generate_json_response


@app.get("/services")
def get_services(date: str = None):
    """Эндпоинт для получения курсов валют и стоимости акций"""
    result = generate_json_response(date)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

#--------------------------------------------------
#----- 15. main------------------------------------
#--------------------------------------------------

import sys
import json
import logging
import os
import pandas as pd
from src.views import generate_main_page_data
from src.services import simple_search, search_by_phone_numbers, analyze_cashback_categories
from src.reports import spending_by_category

# Настройка логирования в файл проекта и консоль
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'project.log')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main_application")


def main():
    logger.info("Приложение успешно запущено.")
    print("=== Финансовый Анализатор ===")
    print("1. Сгенерировать Главную страницу (JSON)")
    print("2. Простой поиск по транзакциям")
    print("3. Поиск транзакций по номерам телефонов")
    print("4. Анализ категорий повышенного кешбэка")
    print("5. Сформировать отчет по категории (Excel)")

    choice = input("\nВыберите действие (1-5): ").strip()

    # Путь к исходной таблице для сервисов поиска
    excel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../data', 'operations.xlsx')

    # Загружаем сырые данные из Excel в список словарей, если файл существует
    raw_data = []
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        # Приводим даты к строке для корректной передачи в сервисы
        if 'Дата операции' in df.columns:
            df['Дата операции'] = df['Дата операции'].astype(str)
        raw_data = df.to_dict(orient='records')

    if choice == '1':
        date_input = input("Введите дату и время (YYYY-MM-DD HH:MM:SS): ").strip()
        # Пример: 2021-12-21 13:00:00
        result = generate_main_page_data(date_input)
        print("\nРезультат (JSON):")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif choice == '2':
        query = input("Введите строку для поиска (Категория/Описание): ").strip()
        result_json = simple_search(raw_data, query)
        print("\nНайденные транзакции:")
        print(result_json)

    elif choice == '3':
        result_json = search_by_phone_numbers(raw_data)
        print("\nТранзакции с телефонными номерами:")
        print(result_json)

    elif choice == '4':
        try:
            year = int(input("Введите год (например, 2021): ").strip())
            month = int(input("Введите месяц (1-12): ").strip())
            result_json = analyze_cashback_categories(raw_data, year, month)
            print("\nАнализ кешбэка по категориям:")
            print(result_json)
        except ValueError:
            print("Ошибка: год и месяц должны быть числами.")

    elif choice == '5':
        if not os.path.exists(excel_path):
            print("Файл базы данных не найден.")
            return
        df_all = pd.read_excel(excel_path)
        category = input("Введите категорию (например, Супермаркеты): ").strip()
        date_opt = input("Введите дату (ДД.ММ.ГГГГ) или нажмите Enter для текущей: ").strip()
        date_param = date_opt if date_opt else None

        # Запуск функции-отчета (декоратор автоматически сохранит файл в data/reports/)
        spending_by_category(df_all, category, date_param)
        print("\nОтчет успешно сформирован и сохранен в папку data/reports/")

    else:
        print("Неверный выбор.")


if __name__ == "__main__":
    main()


