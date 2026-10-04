import pytest

from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)


def test_symbol_is_normalised_and_checked():
    assert validate_symbol(" btcusdt ") == "BTCUSDT"
    with pytest.raises(ValueError):
        validate_symbol("")
    with pytest.raises(ValueError):
        validate_symbol("BTC-USDT")


def test_side_is_case_insensitive_and_restricted():
    assert validate_side("buy") == "BUY"
    with pytest.raises(ValueError):
        validate_side("HOLD")


def test_order_type_is_restricted():
    assert validate_order_type("stop_market") == "STOP_MARKET"
    with pytest.raises(ValueError):
        validate_order_type("OCO")


@pytest.mark.parametrize("bad", ["0", "-1", "abc", ""])
def test_quantity_must_be_a_positive_number(bad):
    with pytest.raises(ValueError):
        validate_quantity(bad)


def test_quantity_keeps_decimal_precision():
    assert validate_quantity("0.001") == "0.001"


def test_price_rules_per_order_type():
    assert validate_price(None, "MARKET") is None
    assert validate_price(None, "STOP_MARKET") is None
    assert validate_price("50000", "LIMIT") == "50000"
    with pytest.raises(ValueError):
        validate_price(None, "LIMIT")
    with pytest.raises(ValueError):
        validate_price("-5", "LIMIT")


def test_stop_price_is_only_required_for_stop_market():
    assert validate_stop_price(None, "LIMIT") is None
    assert validate_stop_price("58000", "STOP_MARKET") == "58000"
    with pytest.raises(ValueError):
        validate_stop_price(None, "STOP_MARKET")
