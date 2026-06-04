#--------------------------------------------------
#----- 4. Веб страницы---ОСНОВНАЯ--API-------------
#--------------------------------------------------

import json
import os
from datetime import datetime

def get_month_range(date_str: str) -> tuple[datetime, datetime]:
    """Вычисляет диапазон от 1-го числа месяца до указанной даты."""
    try:
        end_date = datetime.strptime(date_str, "%d.%m.%Y")
        start_date = end_date.replace(day=1)
        return start_date, end_date
    except ValueError:
        raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГГГ")

def load_user_settings(file_path: str) -> tuple[list[str], list[str]]:
    """Читает пользовательские настройки."""
    if not os.path.exists(file_path):
        return ["USD"], ["AAPL"]
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("user_currencies", []), data.get("user_stocks", [])

#--------------------------------------------------
#----- 6. Веб страницы---доп.ГЛАВНАЯ---------------
#--------------------------------------------------

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


#------заменить по новому условию---из main---------

# def get_greeting(dt: datetime) -> str:
#     """Возвращает приветствие строго по временным интервалам ТЗ."""
#     time_now = dt.time()
#     if datetime.strptime("06:00", "%H:%M").time() <= time_now <= datetime.strptime("11:59", "%H:%M").time():
#         return "Доброе утро"
#     elif datetime.strptime("12:00", "%H:%M").time() <= time_now <= datetime.strptime("17:59", "%H:%M").time():
#         return "Добрый день"
#     elif datetime.strptime("18:00", "%H:%M").time() <= time_now <= datetime.strptime("22:59", "%H:%M").time():
#         return "Добрый вечер"
#     else:
#         return "Доброй ночи"

#--------------------------------------------------



def get_greeting(dt: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = dt.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def parse_incoming_datetime(date_str: str) -> tuple[datetime, datetime]:
    """
    Парсит строку 'YYYY-MM-DD HH:MM:SS'.
    Возвращает объект даты и дату начала этого месяца.
    """
    try:
        end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0)
        return start_date, end_date
    except ValueError as e:
        logger.error(f"Ошибка парсинга даты {date_str}: {e}")
        raise ValueError("Неверный формат. Используйте YYYY-MM-DD HH:MM:SS")

