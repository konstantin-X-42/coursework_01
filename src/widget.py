from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(card_or_account: str) -> str:
    """функция маскирует номер карты или счёта"""
    if "Счет" in card_or_account:
        mask = get_mask_account(card_or_account[5:])
    else:
        mask = get_mask_card_number(card_or_account[-16:])
    return mask


# --------------------------------------------------------------------


def get_date(date_str: str = "") -> str:
    """функция возвращает дату в формате 'ДД.ММ.ГГГГ'"""
    if date_str:
        if type(date_str) is str:
            date_output = date_str[:10]
            date_list = date_output.split("-")  # преобразование в список строк
            for i in date_list:
                if not i.isdecimal():  # в строке только цифры
                    return "Error_07 - в дате не числовой символ"
            if 0 < int(date_list[2]) < 32 and 0 < int(date_list[1]) < 13 and 1900 < int(date_list[0]) < 2100:
                date_list.append(date_list[1])  # добавление элемента с индексом 1 в конец
                date_list.append(date_list[0])  # добавление элемента с индексом 0 в конец
                del date_list[0]
                del date_list[0]
                date_str = ".".join(date_list)
                return date_str
            else:
                return "Error_08 - значения цифр за пределами формата даты"
        else:
            return "Error_09 - введён не допустимый тип данных"
    else:
        return "Error_10 - в функцию подаётся пустая строка"
