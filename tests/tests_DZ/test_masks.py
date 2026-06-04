from src.DZ.masks import get_mask_account, get_mask_card_number


def test_correct_get_mask_card_number(number_card):
    assert get_mask_card_number("7000792289606361") == number_card
    assert get_mask_card_number(7000792289606361) == number_card


def test_not_correct_get_mask_card_number(number_card):
    assert get_mask_card_number("700079228960636") != number_card
    assert get_mask_card_number(700079228960636) != number_card
    assert get_mask_card_number("70007922+9606361") != number_card
    assert get_mask_card_number(70007922 + 9606361) != number_card
    assert get_mask_card_number("70007922889606361") != number_card
    assert get_mask_card_number(70007922889606361) != number_card
    assert get_mask_card_number("h000792289606361") != number_card
    assert get_mask_card_number("-700079228960636") != number_card
    assert get_mask_card_number(-700079228960636) != number_card
    assert get_mask_card_number(["7000792289606361"]) != number_card  # type: ignore
    assert get_mask_card_number([7000792289606361]) != number_card  # type: ignore
    assert get_mask_card_number({"7000792289606361"}) != number_card  # type: ignore
    assert get_mask_card_number({7000792289606361}) != number_card  # type: ignore
    assert get_mask_card_number() != number_card


# --------------------------------------------------------------------


def test_correct_get_mask_account(number_account):
    assert get_mask_account("73654108430135874305") == number_account
    assert get_mask_account(73654108430135874305) == number_account


def test_not_correct_get_mask_account(number_account):
    assert get_mask_account("7365410843013587430") != number_account
    assert get_mask_account(7365410843013587430) != number_account
    assert get_mask_account(73654108401 + 35874305) != number_account
    assert get_mask_account("736541084301358874305") != number_account
    assert get_mask_account(736541084301358874305) != number_account
    assert get_mask_account("736g54108430135874305") != number_account
    assert get_mask_account("s3654108430135874305") != number_account
    assert get_mask_account("-3654108430135874305") != number_account
    assert get_mask_account(-73654108430135874305) != number_account
    assert get_mask_account("736541084/0135874305") != number_account
    assert get_mask_account(["73654108430135874305"]) != number_account  # type: ignore
    assert get_mask_account([73654108430135874305]) != number_account  # type: ignore
    assert get_mask_account({"73654108430135874305"}) != number_account  # type: ignore
    assert get_mask_account({73654108430135874305}) != number_account  # type: ignore
    assert get_mask_account() != number_account
    # assert False
