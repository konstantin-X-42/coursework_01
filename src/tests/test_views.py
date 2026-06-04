#--------------------------------------------------
#----- 8. Веб страницы---доп.ГЛАВНАЯ---------------
#--------------------------------------------------

import pytest
from datetime import datetime
from src.utils import get_greeting
from src.views import generate_main_page_json


def test_get_greeting():
    """Тестирование правильности приветствия по часам."""
    assert get_greeting(datetime(2023, 5, 20, 9, 0, 0)) == "Доброе утро"
    assert get_greeting(datetime(2023, 5, 20, 15, 0, 0)) == "Добрый день"
    assert get_greeting(datetime(2023, 5, 20, 20, 0, 0)) == "Добрый вечер"
    assert get_greeting(datetime(2023, 5, 20, 2, 0, 0)) == "Доброй ночи"


def test_generate_main_page_json_structure():
    """Тестирование структуры ответа главной функции."""
    result = generate_main_page_json("2021-12-21 13:00:00")

    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result
    assert result["greeting"] == "Добрый день"


