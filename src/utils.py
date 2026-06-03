import json
import logging
from pathlib import Path
from typing import Any

# Импортируем функцию настройки логгера из файла log_config текущей директории
from src.log_config import module_logger

# Инициализируем логгер
log = module_logger(
    file_name="utils.log",  # имя файла для записи лога
    logger_name="logs",  # имя папки (директория хранения лог файла)
    log_level=logging.DEBUG,  # уровень логирования DEBUG INFO WARNING ERROR CRITICAL
    overwrite=False,  # предыдущие логи в файле: False - оставить и записать, True - очистить и записать
    log_console=False,  # лог: True - в файл и консоль, False - в файл
)
log.info("Система логирования в модуле utils.py инициализирована успешно")
# -------------------------------------------------------

# Абсолютный путь к папке src, где лежит utils.py для файла JSON
CURRENT_DIR = Path(__file__).resolve().parent


def get_transactions(file: str | Path) -> list[dict[str, Any]]:
    """Читает JSON-файл и возвращает список словарей с транзакциями,
    файл не найден или пуст или содержит не список, возвращает пустой список.
    """
    log.info(f"Функция инициализирована с аргументом: {file}")
    path = Path(file)
    if not path.is_file():
        log.warning("JSON-файл не существует, возвращаем []")
        return []
    try:
        with open(path, "r", encoding="utf-8") as json_file:  # открываем JSON-файл на чтение
            data = json.load(json_file)  # читаем JSON-файл и преобразуем в тип данных Python
            if isinstance(data, list):  # обрабатываем только тип данных List[]
                log.info("Успешно")
                return data
            log.warning(f"Функция обрабатывает: <class 'list'>, тип данных JSON-файла: {type(data)}, возвращаем []")
            return []  # иной тип данных, не list - ошибка
    except json.JSONDecodeError, FileNotFoundError:
        log.critical("Содержимое JSON-файла повреждено или JSON-файл отсутствует, возвращаем []")
        return []


# -----------вызываем функцию------------
# Относительный путь от корня проекта
# path_to_file = "../data_13_2_10/operations.json"

# Абсолютный путь к файлу operations.json
# path_to_file = CURRENT_DIR.parent / "data_13_2_10" / "operations.json"

# print(get_transactions(path_to_file))
