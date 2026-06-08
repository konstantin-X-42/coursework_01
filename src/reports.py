# --------------------------------------------------
# ----- 11. Сервисы---ОСНОВНАЯ----------------------
# --------------------------------------------------

import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps

import pandas as pd

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def save_report_to_file(filename=None):
    """
    Декоратор для функций-отчетов.
    Если вызван без параметров (@save_report_to_file), сохраняет в файл по умолчанию.
    Если вызван с параметром (@save_report_to_file("my_report.xlsx")), сохраняет в указанный файл.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Вызываем саму функцию отчета, она должна возвращать pandas.DataFrame
            df = func(*args, **kwargs)

            # Определяем имя файла
            if filename is None:
                # Имя по умолчанию: report_названиеФункции_датаВремя.xlsx
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                actual_filename = f"report_{func.__name__}_{timestamp}.xlsx"
            else:
                actual_filename = filename

            file_path = os.path.join(REPORTS_DIR, actual_filename)

            try:
                logger.info(f"Декоратор сохраняет отчет в файл: {file_path}")
                # Сохраняем результат работы функции (DataFrame) в Excel
                df.to_excel(file_path, index=False)
                logger.info(f"Отчет успешно сохранен.")
            except Exception as e:
                logger.error(f"Не удалось сохранить отчет в файл: {e}")

            return df

        return wrapper

    # если декоратор вызван без скобок @save_report_to_file,
    # то первым аргументом `filename` придет сама декорируемая функция
    if callable(filename):
        func = filename
        filename = None
        return decorator(func)

    return decorator


@save_report_to_file
def report_spending_by_category(
    df: pd.DataFrame, category: str, date_str: str = None
) -> pd.DataFrame:
    """
    Отчет: Траты по заданной категории за последние 3 месяца от указанной даты.
    Если date_str не указана, берется текущая дата.
    """
    logger.info(f"Генерация отчета по категории '{category}' за последние 3 месяца.")

    if df.empty:
        logger.warning("Передан пустой DataFrame.")
        return pd.DataFrame()

    # Определяем конечную дату для анализа
    if date_str:
        end_date = pd.to_datetime(date_str, dayfirst=True)
    else:
        end_date = pd.Timestamp.now()

    # Начальная дата — ровно 3 месяца назад
    start_date = end_date - timedelta(days=90)

    # Копируем и приводим колонку с датами к типу datetime
    df_temp = df.copy()
    df_temp["Дата операции"] = pd.to_datetime(df_temp["Дата операции"], dayfirst=True)

    # Фильтруем по дате, категории и оставляем только расходы (Сумма платежа < 0)
    mask = (
        (df_temp["Дата операции"] >= start_date)
        & (df_temp["Дата операции"] <= end_date)
        & (df_temp["Категория"].str.lower() == category.lower())
        & (df_temp["Сумма платежа"] < 0)
    )

    result_df = df_temp[mask]
    logger.info(f"Отчет сформирован. Найдено строк: {len(result_df)}")
    return result_df


# ==================================================
# ЗАПУСК функции-декоратор   save_report_to_file()
# ==================================================

# if __name__ == "__main__":
#     import shutil
#
#     print("=== ЗАПУСК ФУНКЦИИ-ДЕКОРАТОРА    save_report_to_file() ===")
#
#     # Создаем базовый тестовый датафрейм
#     test_df = pd.DataFrame({"Дата операции": ["01.06.2026"], "Категория": ["Тест"], "Сумма платежа": [-100]})
#
#     # ----------------------------------------------------
#     # Тест 1: Проверка вызова БЕЗ СКОБОК @save_report_to_file
#     # Имя файла должно сгенерироваться автоматически
#     # ----------------------------------------------------
#     print("\n[Тест 1] Запуск функции с декоратором без параметров...")
#
#     # Наша функция report_spending_by_category уже обернута так
#     report_spending_by_category(test_df, "Тест", "01.06.2026")
#
#     # Проверяем, появился ли файл в папке REPORTS_DIR
#     files_in_dir = os.listdir(REPORTS_DIR)
#     auto_report_file = [f for f in files_in_dir if f.startswith("report_report_spending_by_category_")]
#
#     if auto_report_file:
#         print(f"✅ Успех! Создан файл с автоматическим именем: {auto_report_file[0]}")
#     else:
#         print("❌ Ошибка: Файл с автоматическим именем не найден!")
#
#     # ----------------------------------------------------
#     # Тест 2: Проверка вызова С ПАРАМЕТРАМИ @save_report_to_file("...")
#     # Имя файла должно быть строго кастомным
#     # ----------------------------------------------------
#     print("\n[Тест 2] Запуск функции с кастомным именем файла...")
#
#     custom_filename = "quick_test_custom_report.xlsx"
#
#
#     # На ходу создаем и декорируем тестовую функцию
#     @save_report_to_file(custom_filename)
#     def dummy_custom_report(df):
#         return df
#
#
#     dummy_custom_report(test_df)
#
#     custom_file_path = os.path.join(REPORTS_DIR, custom_filename)
#     if os.path.exists(custom_file_path):
#         print(f"✅ Успех! Создан файл с кастомным именем: {custom_filename}")
#         # Удаляем временный кастомный файл, чтобы не мусорить
#         os.remove(custom_file_path)
#     else:
#         print("❌ Ошибка: Кастомный файл не был создан!")
#
#     # ----------------------------------------------------
#     # Тест 3: Проверка сохранения контекста оригинальной функции (@wraps)
#     # ----------------------------------------------------
#     print("\n[Тест 3] Проверка сохранения метаданных функции (__name__)...")
#     if report_spending_by_category.__name__ == "report_spending_by_category":
#         print("✅ Успех! @wraps корректно сохранил имя оригинальной функции.")
#     else:
#         print(f"❌ Ошибка! Имя функции испорчено декоратором: {report_spending_by_category.__name__}")
#
#     print("\n=== ПРОВЕРКА ДЕКОРАТОРА ЗАВЕРШЕНА ===")

# --------------------------------------------------
# ----- 12. Сервисы---Доп Траты по категории--------
# --------------------------------------------------

import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from src.reports import save_report_to_file


@save_report_to_file
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца от переданной даты.
    Если дата не передана, то берется текущая дата.
    """
    logger.info(f"Старт генерации отчета 'Траты по категории' для: '{category}'")

    if transactions.empty:
        logger.warning("Передан пустой датафрейм с транзакциями.")
        return pd.DataFrame()

    # 1. Определение целевой (конечной) даты
    if date:
        try:
            # Поддерживаем форматы дат ДД.ММ.ГГГГ или ГГГГ-ММ-ДД
            if "-" in date:
                end_date = pd.to_datetime(
                    date, format="%Y-%m-%d %H:%M:%S", errors="ignore"
                )
                if isinstance(end_date, str):
                    end_date = pd.to_datetime(date, format="%Y-%m-%d")
            else:
                end_date = pd.to_datetime(date, dayfirst=True)
            logger.info(
                f"Используется переданная дата для анализа: {end_date.strftime('%Y-%m-%d')}"
            )
        except Exception as e:
            logger.error(
                f"Ошибка парсинга переданной даты '{date}': {e}. Берем текущую дату."
            )
            end_date = pd.Timestamp.now()
    else:
        end_date = pd.Timestamp.now()
        logger.info(
            f"Дата не передана. Используется текущая дата: {end_date.strftime('%Y-%m-%d')}"
        )

    # 2. Точный расчет даты 3 месяца назад с помощью DateOffset (учитывает разное количество дней в месяцах)
    start_date = end_date - pd.DateOffset(months=3)
    logger.info(
        f"Временной интервал анализа: с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}"
    )

    # 3. Подготовка данных
    df_temp = transactions.copy()
    df_temp["Дата операции"] = pd.to_datetime(
        df_temp["Дата операции"], dayfirst=True, errors="coerce"
    )

    # 4. Фильтрация: диапазон дат, совпадение категории (без учета регистра) и только расходы (< 0)
    mask = (
        (df_temp["Дата операции"] >= start_date)
        & (df_temp["Дата операции"] <= end_date)
        & (df_temp["Категория"].str.lower() == category.lower())
        & (df_temp["Сумма платежа"] < 0)
    )

    result_df = df_temp[mask]
    logger.info(f"Отчет успешно сформирован. Найдено транзакций: {len(result_df)}")

    # Возвращаем отфильтрованный DataFrame (декоратор автоматически сохранит его в Excel)
    return result_df  # type: ignore


# ==================================================
# ЗАПУСК функции-декоратор   spending_by_category()
# ==================================================

# if __name__ == "__main__":
#     import os
#
#     # Настраиваем базовый вывод логов в консоль, чтобы видеть шаги выполнения
#     logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
#
#     print("\n=== ЗАПУСК ПРОВЕРКИ ФУНКЦИИ-ДЕКОРАТОРА    spending_by_category() ===")
#
#     # 1. Формируем тестовые данные транзакций (Используем текущий 2026 год)
#     # Текущая дата для тестов: 07.06.2026. Окно в 3 месяца: с 07.03.2026 по 07.06.2026
#     test_data = {
#         "Дата операции": [
#             "05.06.2026 14:20:00",  # Внутри окна (Июнь)
#             "15.04.2026 09:00:00",  # Внутри окна (Апрель)
#             "10.01.2026 18:45:00",  # Вне окна (Январь — больше 3 месяцев назад)
#             "20.05.2026 12:00:00"  # Внутри окна, но другая категория
#         ],
#         "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты", "Одежда"],
#         "Сумма платежа": [-1500.50, -450.00, -3000.00, -5000.00]
#     }
#     df_transactions = pd.DataFrame(test_data)
#
#     # 2. Вызов функции с автоматическим срабатыванием декоратора
#     # Анализируем категорию "Супермаркеты" относительно даты "07.06.2026"
#     target_category = "Супермаркеты"
#     analysis_date = "07.06.2026"
#
#     print(f"\n[Шаг 1] Вызываем функцию spending_by_category для категории '{target_category}'...")
#     filtered_df = spending_by_category(df_transactions, category=target_category, date=analysis_date)
#
#     # 3. Проверка корректности фильтрации Pandas dataframe
#     print("\n[Шаг 2] Проверяем результат фильтрации в памяти:")
#     print(filtered_df)
#
#     # Ожидаем ровно 2 транзакции (июнь и апрель). Январь отсекается по DateOffset(months=3)
#     assert len(filtered_df) == 2, f"❌ Ошибка фильтрации! Ожидалось 2 строки, получено {len(filtered_df)}"
#     print("✅ Фильтрация данных по дате, категории и значению расхода сработала верно.")
#
#     # 4. Проверка работы декоратора (проверяем физическое создание файла Excel)
#     print("\n[Шаг 3] Проверяем, сохранил ли декоратор файл на диск...")
#
#     # Импортируем путь директории из модуля с декоратором для валидации
#     from src.reports import REPORTS_DIR
#
#     if os.path.exists(REPORTS_DIR):
#         files = os.listdir(REPORTS_DIR)
#         # Ищем файл, чье имя начинается со строгого паттерна нашей новой функции
#         generated_files = [f for f in files if f.startswith("report_spending_by_category_")]
#
#         if generated_files:
#             print(f"✅ Успех! Декоратор перехватил управление и создал файл: {generated_files[-1]}")
#         else:
#             print("❌ Ошибка! Функция отработала, но файл в директории отчетов не найден.")
#     else:
#         print(f"❌ Ошибка! Директория для отчетов не существует по пути: {REPORTS_DIR}")
#
#     print("\n=== ПРОВЕРКА ДЕКОРАТОРА И ФУНКЦИИ УСПЕШНО ЗАВЕРШЕНА ===")
