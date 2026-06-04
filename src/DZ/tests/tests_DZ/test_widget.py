import pytest

from src.DZ.widget import get_date, mask_account_card


# параметризация теста все пишется в модуле test_... (conftest.py только для фикстур)
@pytest.mark.parametrize(
    "input_string, expected_result",
    [
        ("Maestro 1596837868705199", "1596 83** **** 5199"),
        ("MasterCard 7158300734726758", "7158 30** **** 6758"),
        ("Visa Classic 6831983878705199", "6831 98** **** 5199"),
        ("Visa Platinum 8990922113665229", "8990 92** **** 5229"),
        ("Visa Gold 5999414228426353", "5999 41** **** 6353"),
        ("Счет 64686473678894779589", "** 9589"),
        ("Счет 35383033474447895560", "** 5560"),
        ("Счет 73654108430135874305", "** 4305"),
    ],
)
def test_correct_get_mask_card_number(input_string, expected_result):
    assert mask_account_card(input_string) == expected_result


# --------------------------------------------------------------------


def test_correct_get_date(date_str):
    assert get_date("2024-03-11T02:26:18.671407") == date_str


def test_not_correct_get_date(date_str):
    assert get_date("2024-g3-11T02:26:18.671407") != date_str
    assert get_date("2024-33-11T02:26:18.671407") != date_str
    assert get_date("2024-33-11T02:26:18.671407") != date_str
    assert get_date("1024-03-11T02:26:18.671407") != date_str
    assert get_date("2024-03-32T02:26:18.671407") != date_str
    assert get_date(20240311022618671407) != date_str  # type: ignore
    assert get_date([20240311022618671407]) != date_str  # type: ignore
    assert get_date({20240311022618671407}) != date_str  # type: ignore
    assert get_date() != date_str
