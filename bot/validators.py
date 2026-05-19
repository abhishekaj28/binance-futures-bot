"""
validators.py
-------------
Pure-Python validation helpers for CLI inputs.
All functions raise ValueError with a human-readable message on failure.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional


SUPPORTED_SIDES = {"BUY", "SELL"}
SUPPORTED_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}  # extendable


def validate_symbol(symbol: str) -> str:
    """Symbol must be a non-empty alphanumeric string (e.g. BTCUSDT)."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if not symbol.isalnum():
        raise ValueError(f"Symbol '{symbol}' must be alphanumeric (e.g. BTCUSDT).")
    return symbol


def validate_side(side: str) -> str:
    """Side must be BUY or SELL (case-insensitive)."""
    side = side.strip().upper()
    if side not in SUPPORTED_SIDES:
        raise ValueError(f"Side must be one of {SUPPORTED_SIDES}, got '{side}'.")
    return side


def validate_order_type(order_type: str) -> str:
    """Order type must be MARKET, LIMIT, or STOP_MARKET."""
    order_type = order_type.strip().upper()
    if order_type not in SUPPORTED_ORDER_TYPES:
        raise ValueError(
            f"Order type must be one of {SUPPORTED_ORDER_TYPES}, got '{order_type}'."
        )
    return order_type


def validate_quantity(quantity: str) -> str:
    """Quantity must be a positive decimal number."""
    try:
        qty = Decimal(str(quantity))
    except InvalidOperation:
        raise ValueError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be > 0, got {qty}.")
    return str(qty)


def validate_price(price: Optional[str], order_type: str) -> Optional[str]:
    if order_type in {"MARKET", "STOP_MARKET"}:
        return None
    """
    Price is required for LIMIT orders and must be a positive decimal.
    For MARKET orders it is ignored (returns None).
    """
    if order_type == "MARKET":
        return None  # price is irrelevant for market orders

    if price is None or str(price).strip() == "":
        raise ValueError("Price is required for LIMIT orders.")

    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValueError(f"Price '{price}' is not a valid number.")
    if p <= 0:
        raise ValueError(f"Price must be > 0, got {p}.")
    return str(p)


def validate_stop_price(stop_price: Optional[str], order_type: str) -> Optional[str]:
    """Stop price is required for STOP_MARKET orders."""
    if order_type != "STOP_MARKET":
        return None
    if stop_price is None or str(stop_price).strip() == "":
        raise ValueError("Stop price is required for STOP_MARKET orders.")
    try:
        sp = Decimal(str(stop_price))
    except InvalidOperation:
        raise ValueError(f"Stop price '{stop_price}' is not a valid number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be > 0, got {sp}.")
    return str(sp)

