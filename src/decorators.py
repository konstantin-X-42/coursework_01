import datetime
from functools import wraps


def log(filename=None):  # type: ignore
    """
    Декоратор для логирования работы функций.
    :param filename: Путь к файлу лога. Если None, вывод только в консоль.
    """

    def decorator(func):  # type: ignore
        @wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            # фиксируем время обращения к декоратору в формате Г.М.Д Ч:М:С:млС
            log_date = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S:%f")[:-3]
            try:
                result = func(*args, **kwargs)
                # сообщение в лог, дата и время, название функции, позиционные и именованные аргументы, успешно
                log_message = f"{log_date} >>> {func.__name__} >>> ok\n"
                # функция внутренняя _write_log(), записывает текст log_message, по адресу filename -текущая директория
                _write_log(log_message, filename)  # type: ignore
                return result

            except Exception as e:  # Если произошла ошибка фиксируем в лог
                # сообщение в лог, дата и время, название функции, позиционные и именованные аргументы, тип ошибки
                log_message = f"{log_date} >>> {func.__name__} >>> error: {type(e).__name__}\n"

                _write_log(log_message, filename)  # type: ignore  # записываем в лог
                raise e  # Пробрасываем ошибку дальше

        return wrapper

    return decorator


def _write_log(message, filename):  # type: ignore
    """вспомогательная функция записи лога в файл или в консоль"""
    if filename:
        # откроет файл, приготовится к записи данных, режим "a" в самый конец
        with open(filename, "a", encoding="utf-8") as f:
            f.write(message)  # запись текста в файл
    else:
        print(message.strip())  # вывод сообщения на экран
