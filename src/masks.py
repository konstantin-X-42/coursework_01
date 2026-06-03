import logging

# Импортируем функцию настройки логгера из файла log_config абсолютный путь
from src.log_config import module_logger

# Инициализируем логгер
log = module_logger(
    file_name="masks.log",  # имя файла для записи лога
    logger_name="logs",  # имя папки (директория хранения лог файла)
    log_level=logging.DEBUG,  # уровень логирования DEBUG INFO WARNING ERROR CRITICAL
    overwrite=False,  # предыдущие логи в файле: False - оставить и записать, True - очистить и записать
    log_console=False,  # лог: True - в файл и консоль, False - в файл
)
log.info("Система логирования в модуле masks.py инициализирована успешно")


def get_mask_card_number(number_card: str | int = -1) -> str:
    """функция возвращает скрытый номер карты в виде: 8990 92** **** 5229"""
    log.info("Функция инициализирована")
    if number_card != -1:
        if str(number_card).isdecimal():  # в строке только цифры
            counter = 0
            step = 4
            number_cart_mask = ""
            for i in str(number_card):
                counter += 1
                if 6 < counter < 13:
                    i = "*"
                number_cart_mask += i
                if step == counter != 16:
                    step += 4
                    number_cart_mask += " "
            if counter != 16:
                log.critical(
                    f"Error_01 - не верное количество символов в номере карты, получено: {len(str(number_card))} элем."
                )
                return "Error_01 - не верное количество символов в номере карты"
        else:
            log.critical("Error_02 - введён не допустимый тип данных или не числовой символ в номере карты")
            return "Error_02 - введён не допустимый тип данных или не числовой символ в номере карты"
    else:
        log.critical("Error_03 - не введён номер карты")
        return "Error_03 - не введён номер карты"
    log.info("Успешно")
    return number_cart_mask


# -----------вызываем функцию------------
# print(get_mask_card_number('7000792289606361'))
# --------------------------------------------------------------------


def get_mask_account(number_account: str | int = -1) -> str:
    """функция возвращает скрытый номер счёта в виде: ** 5560"""
    log.info("Функция инициализирована")
    if number_account != -1:
        if str(number_account).isdecimal():  # в строке только цифры
            counter = 0
            step = 4
            number_account_mask = ""
            for i in str(number_account):
                counter += 1
                if 14 < counter < 17:
                    i = "*"
                if counter > 14:
                    number_account_mask += i
                if step == counter != 20:
                    step += 4
                    if 14 < counter:  # исключаем пробелы первых 3-х step
                        number_account_mask += " "  # при выполнении добавляем пробел с шагом в 4 символа
            if counter != 20:
                log.critical(
                    f"Error_04 - не верное количество символов в номере счёта, получено: {len(str(number_account))} эл"
                )
                return "Error_04 - не верное количество символов в номере счёта"
        else:
            log.critical("Error_05 - введён не допустимый тип данных или не числовой символ в номере счёта")
            return "Error_05 - введён не допустимый тип данных или не числовой символ в номере счёта"
    else:
        log.critical("Error_06 - не введён номер счёта")
        return "Error_06 - не введён номер счёта"
    log.info("Успешно")
    return number_account_mask


# -----------вызываем функцию------------
# get_mask_account("73654108430135584305")
