import os

import pytest

from src.decorators import log  # импортируем функцию log из модуля decorators

"""
КАМАНДА ЗАПУСКАЕТ ТЕСТ в консоль из МОДУЛЯ test_decorators
pytest tests/test_decorators.py

ошибку в консоль
pytest -s tests/test_decorators.py

покрытие тестами модуля "src" в консоль
pytest --cov=src tests/

покрытие тестами модуля "src" в html
pytest --cov=src --cov-report=html tests/
"""

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


@log(filename="tests/test_log.txt")  # type: ignore
def divide_log(a, b):
    return a / b


def test_divide_error_log():
    """проверяем функцию-декоратор на обработку ошибки, деление ноль и запись в log"""
    with pytest.raises(ZeroDivisionError):
        divide_log(10, 0)  # В файл запишется время, название функции и Inputs: (10, 0) тип ошибки


# Выведет в test_log: 2026.05.11 17:49:56:731 >>> divide_log >>> error: ZeroDivisionError

# ----------------------------


@log(filename=None)  # type: ignore
def divide_consol(a, b):
    return a / b


def test_divide_error_consol():
    """проверяем функцию-декоратор на обработку ошибки, деление ноль и запись в консоль"""
    with pytest.raises(ZeroDivisionError):
        divide_consol(10, 0)  # В файл запишется время, название функции и Inputs: (10, 0) тип ошибки


# Выведет в консоль tests\test_decorators.py .2026.05.11 17:44:25:538 >>> divide_consol >>> error: ZeroDivisionError


# ----------------------------


@log(filename="tests/test_log.txt")  # type: ignore
def divide_hello(name):
    """проверяем функцию-декоратор на верную отработку и запись в log"""
    return f"Привет, {name}!"


divide_hello("Алексей")
# Выведет в test_log: 2026.05.11 17:42:50:649 >>> divide_hello >>> ok

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


# 1. Тестирование вывода в консоль (capsys)
def test_log_console_output(capsys):
    """проверяем функцию-декоратор на отсутствие ошибки в работе и правильную запись в консоль (capsys)"""

    @log(filename=None)  # type: ignore
    def divide_console_capsys(a, b):
        return a * b

    divide_console_capsys(2, 3)

    # перехватываем вывод данных в консоль.
    captured = capsys.readouterr()

    # Проверяем, что в выводе есть имя функции и статус
    assert "divide_console_capsys" in captured.out
    assert "ok" in captured.out
    assert "202" in captured.out  # проверка наличия года в дате


# ----------------------------


# 2. Тестирование записи в файл
def test_log_file_output():
    test_file = "tests/test_log.txt"

    # # Удаляем файл перед тестом, от прошлых запусков
    # if os.path.exists(test_file):
    #     os.remove(test_file)

    @log(filename=test_file)  # type: ignore
    def add(a, b):
        return a + b

    add(10, 20)

    # Проверяем, что файл создался и содержит нужные данные
    assert os.path.exists(test_file)
    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "add" in content  # проверка названия функции
        assert "ok" in content


# ----------------------------


# 3. Тестирование записи ошибки в лог-файл
def test_log_error_to_file():
    test_file = "tests/test_log.txt"

    @log(filename=test_file)  # type: ignore
    def divide(a, b):
        return a / b

    # Проверяем, ошибка пробрасывается дальше и фиксируется в файле
    with pytest.raises(ZeroDivisionError):  # проверяем ошибка пробрасывается дальше
        divide(1, 0)

    with open(test_file, "r", encoding="utf-8") as f:  # проверяем ошибка зафиксирована в файле
        content = f.read()
        assert "divide" in content
        assert "error: ZeroDivisionError" in content

    # # Удаляем файл после теста
    # if os.path.exists(test_file):
    #     os.remove(test_file)
