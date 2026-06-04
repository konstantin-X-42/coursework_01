#--------------------------------------------------
#----- 11. Сервисы---ОСНОВНАЯ----------------------
#--------------------------------------------------

import os
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
import pandas as pd

logger = logging.getLogger(__name__)

# Папка для сохранения отчетов по умолчанию в корне проекта
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'reports')
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
def report_spending_by_category(df: pd.DataFrame, category: str, date_str: str = None) -> pd.DataFrame:
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
    df_temp['Дата операции'] = pd.to_datetime(df_temp['Дата операции'], dayfirst=True)

    # Фильтруем по дате, категории и оставляем только расходы (Сумма платежа < 0)
    mask = (
            (df_temp['Дата операции'] >= start_date) &
            (df_temp['Дата операции'] <= end_date) &
            (df_temp['Категория'].str.lower() == category.lower()) &
            (df_temp['Сумма платежа'] < 0)
    )

    result_df = df_temp[mask]
    logger.info(f"Отчет сформирован. Найдено строк: {len(result_df)}")
    return result_df

#--------------------------------------------------
#----- 12. Сервисы---Доп Траты по категории--------
#--------------------------------------------------

import logging
from typing import Optional
from datetime import datetime
import pandas as pd
from src.reports import save_report_to_file  # Наш декоратор из прошлого шага

logger = logging.getLogger(__name__)


@save_report_to_file
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
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
                end_date = pd.to_datetime(date, format="%Y-%m-%d %H:%M:%S", errors='ignore')
                if isinstance(end_date, str):
                    end_date = pd.to_datetime(date, format="%Y-%m-%d")
            else:
                end_date = pd.to_datetime(date, dayfirst=True)
            logger.info(f"Используется переданная дата для анализа: {end_date.strftime('%Y-%m-%d')}")
        except Exception as e:
            logger.error(f"Ошибка парсинга переданной даты '{date}': {e}. Берем текущую дату.")
            end_date = pd.Timestamp.now()
    else:
        end_date = pd.Timestamp.now()
        logger.info(f"Дата не передана. Используется текущая дата: {end_date.strftime('%Y-%m-%d')}")

    # 2. Точный расчет даты 3 месяца назад с помощью DateOffset (учитывает разное количество дней в месяцах)
    start_date = end_date - pd.DateOffset(months=3)
    logger.info(f"Временной интервал анализа: с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}")

    # 3. Подготовка данных
    df_temp = transactions.copy()
    df_temp['Дата операции'] = pd.to_datetime(df_temp['Дата операции'], dayfirst=True, errors='coerce')

    # 4. Фильтрация: диапазон дат, совпадение категории (без учета регистра) и только расходы (< 0)
    mask = (
            (df_temp['Дата операции'] >= start_date) &
            (df_temp['Дата операции'] <= end_date) &
            (df_temp['Категория'].str.lower() == category.lower()) &
            (df_temp['Сумма платежа'] < 0)
    )

    result_df = df_temp[mask]
    logger.info(f"Отчет успешно сформирован. Найдено транзакций: {len(result_df)}")

    # Возвращаем отфильтрованный DataFrame (декоратор автоматически сохранит его в Excel)
    return result_df


