#--------------------------------------------------
#----- 11. Сервисы---ОСНОВНАЯ----------------------
#--------------------------------------------------

import os
import pytest
import pandas as pd
from datetime import datetime
from src.reports import report_spending_by_category, save_report_to_file


@pytest.fixture
def sample_dataframe():
    """Создает тестовый Excel-датафрейм."""
    data = {
        'Дата операции': ['01.12.2021', '15.11.2021', '01.05.2021', '20.12.2021'],
        'Категория': ['Супермаркеты', 'Супермаркеты', 'Супермаркеты', 'Фастфуд'],
        'Сумма платежа': [-1000, -500, -2000, -300]
    }
    return pd.DataFrame(data)


def test_report_spending_by_category_filtering(sample_dataframe):
    """Проверяет правильность фильтрации за последние 3 месяца по категории."""
    # Анализируем от даты 25.12.2021.
    # В диапазон 3 месяцев назад попадут 01.12.2021 и 15.11.2021.
    # Запись от 01.05.2021 отсеется по дате. Фастфуд отсеется по категории.
    result = report_spending_by_category(sample_dataframe, category="Супермаркеты", date_str="25.12.2021")

    assert len(result) == 2
    assert all(result['Категория'] == 'Супермаркеты')
    assert -1000 in result['Сумма платежа'].values


def test_decorator_saves_file(sample_dataframe, tmp_path, monkeypatch):
    """Проверяет, что декоратор успешно создает файл."""
    # Перенаправляем папку сохранения отчетов во временную тестовую папку
    monkeypatch.setattr("src.reports.REPORTS_DIR", str(tmp_path))

    # Создаем тестовую функцию с кастомным именем файла внутри декоратора
    @save_report_to_file("test_output.xlsx")
    def dummy_report(df):
        return df

    dummy_report(sample_dataframe)

    expected_file = tmp_path / "test_output.xlsx"
    assert expected_file.exists()

#--------------------------------------------------
#----- 12. Сервисы---Доп Траты по категории--------
#--------------------------------------------------

import pytest
import pandas as pd
from src.reports import spending_by_category

def test_spending_by_category_three_months():
    # Создаем тестовый датафрейм
    data = {
        'Дата операции': [
            '20.12.2021',  # Внутри периода (1 день назад от целевой)
            '20.10.2021',  # Внутри периода (2 месяца назад от целевой)
            '15.09.2021',  # За пределами периода (больше 3 месяцев назад от целевой)
            '21.12.2021'   # Внутри периода, но другая категория
        ],
        'Категория': ['Супермаркеты', 'Супермаркеты', 'Супермаркеты', 'Фастфуд'],
        'Сумма платежа': [-1000.0, -500.0, -2000.0, -300.0]
    }
    df = pd.DataFrame(data)

    # Фильтруем от даты 21.12.2021 по категории "Супермаркеты"
    # Должны остаться только транзакции от 20.12 и 20.10. Транзакция от 15.09 отсекается (прошло > 3 месяцев)
    result = spending_by_category(df, category="Супермаркеты", date="21.12.2021")

    assert len(result) == 2
    assert -1000.0 in result['Сумма платежа'].values
    assert -500.0 in result['Сумма платежа'].values
    assert -2000.0 not in result['Сумма платежа'].values  # Старая транзакция отсеялась

