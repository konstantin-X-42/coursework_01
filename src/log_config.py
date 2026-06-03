import logging
import os


def module_logger(
    file_name: str = "logs.log",
    logger_name: str = "logs",
    log_level: int = logging.DEBUG,
    overwrite: bool = False,
    log_console: bool = False,
) -> logging.Logger:
    """Функция для настройки логгера с динамическим именем файла,
    и именными аргументами - тогда все логи в один файл, False - хранить предыдущий лог,
    False - запрет вывода лога в консоль"""

    logger = logging.getLogger(logger_name)  # создаем или возвращаем существующий логгер с установленным именем

    # ПРОВЕРКА: Если у логгера уже есть обработчики, значит логгер настроен
    # возвращаем логгер, чтобы не добавились дублирующие файлы и консоли
    if logger.handlers:
        return logger

    logger.setLevel(log_level)  # выставляем уровень логирования DEBUG INFO WARNING ERROR CRITICAL

    path_log = f"logs/{file_name}"  # динамический относительный путь хранения файла лога
    abs_file_path = os.path.abspath(path_log)  # определяем абсолютный путь к файлу логов
    abs_dir_path = os.path.dirname(abs_file_path)  # извлекаем путь к ПАПКЕ из абсолютного пути файла
    os.makedirs(abs_dir_path, exist_ok=True)  # если папки logs нет создаём, если есть пропускаем

    # общий формат записи для всех
    file_formater = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)s - строка: %(lineno)d >>> %(message)s"
    )  # шаблон-маска записи в лог

    # РЕЖИМ ЗАПИСИ при запуске logger():
    # True - 'w' (перед записью, удалить старые логи в файле),
    # False - 'a' (продолжить запись не удаляя предыдущие)
    log_mode = "w" if overwrite else "a"

    # запись лога в файл
    file_handler = logging.FileHandler(
        abs_file_path, encoding="utf-8", mode=log_mode
    )  # отправка лога, в кодировке, управление архивом запись
    file_handler.setFormatter(file_formater)  # передаём шаблон записи лога на запись в файл
    logger.addHandler(file_handler)  # записываем лог в файл

    # вывод лога в консоль
    if log_console:  # True — выводить в консоль и файл, False — только в файл
        console_handler = logging.StreamHandler()  # создаем обработчик для вывода логов в консоль
        console_handler.setFormatter(file_formater)  # передаем ему тот же формат строки
        logger.addHandler(console_handler)  # подключаем вывод в консоль к логгеру
    return logger  # возвращаем настроенный логгер


# -------------------------------------------------------
# import logging

# # Импортируем функцию настройки логгера из файла log_config абсолютный путь
# from src.log_config import module_logger

# # Импортируем функцию настройки логгера из файла log_config на один уровень выше (в корне проекта)
# from ..log_config import module_logger

# # Импортируем функцию настройки логгера из файла log_config из папке: основное_окружение/имя папки
# from ИМЯ_ПАПКИ_(директории).log_config import module_logger

# # Инициализируем логгер
# log = module_logger(
#     file_name="logs.log", # имя файла для записи лога
#     logger_name='logs',   # имя папки (директория хранения лог файла)
#     log_level=logging.DEBUG, # уровень логирования DEBUG INFO WARNING ERROR CRITICAL
#     overwrite=False, # предыдущие логи в файле: False - оставить и записать, True - очистить и записать
#     log_console=False, # лог: True - в файл и консоль, False - в файл
# )
# log.info("Система логирования в модуле ИМЯ_МОДУЛЯ инициализирована успешно")
# -------------------------------------------------------
# --- ПРИМЕР ИСПОЛЬЗОВАНИЯ ---
# log.info(f"Функция инициализирована с аргументом: {file}")
# log.info("Программа успешно запустилась!")
# log.warning("Это предупреждение (появится и в консоли, и в файле).")
