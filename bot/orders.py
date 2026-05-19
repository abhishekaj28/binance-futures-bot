"""
orders.py
---------
High-level order placement logic built on top of BinanceFuturesClient.

This layer:
  - Accepts validated parameters
  - Constructs the correct payload per order type
  - Pretty-prints order summaries and responses
  - Returns a structured result dict
"""

import logging
from typing import Any, Dict, Optional

from bot.client import BinanceFuturesClient, BinanceAPIError

logger = logging.getLogger(__name__)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _print_divider(char: str = "─", width: int = 60) -> None:
    print(char * width)


def _print_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> None:
    """Print a formatted summary of what we're about to send."""
    _print_divider()
    print("  📤  ORDER REQUEST SUMMARY")
    _print_divider()
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price:
        print(f"  Price      : {price}")
    if stop_price:
        print(f"  Stop Price : {stop_price}")
    _print_divider()


def _print_order_response(response: Dict[str, Any]) -> None:
    """Print the key fields from Binance's order response."""
    _print_divider()
    print("  📥  ORDER RESPONSE")
    _print_divider()
    print(f"  Order ID     : {response.get('orderId', 'N/A')}")
    print(f"  Client OID   : {response.get('clientOrderId', 'N/A')}")
    print(f"  Symbol       : {response.get('symbol', 'N/A')}")
    print(f"  Side         : {response.get('side', 'N/A')}")
    print(f"  Type         : {response.get('type', 'N/A')}")
    print(f"  Status       : {response.get('status', 'N/A')}")
    print(f"  Orig Qty     : {response.get('origQty', 'N/A')}")
    print(f"  Executed Qty : {response.get('executedQty', 'N/A')}")

    avg_price = response.get("avgPrice") or response.get("price", "N/A")
    print(f"  Avg Price    : {avg_price}")

    time_ms = response.get("updateTime") or response.get("time")
    if time_ms:
        import datetime
        ts = datetime.datetime.utcfromtimestamp(time_ms / 1000).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
        print(f"  Timestamp    : {ts}")
    _print_divider()


# ── Order placement functions ────────────────────────────────────────────────

def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: str,
) -> Dict[str, Any]:
    """
    Place a MARKET order.

    Market orders execute immediately at the best available price.
    No price parameter is needed or accepted.
    """
    _print_order_request(symbol, side, "MARKET", quantity)

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
        )
        _print_order_response(response)
        print("  ✅  Market order placed successfully!\n")
        logger.info(
            "Market order SUCCESS | orderId=%s status=%s executedQty=%s",
            response.get("orderId"),
            response.get("status"),
            response.get("executedQty"),
        )
        return {"success": True, "response": response}

    except BinanceAPIError as exc:
        print(f"  ❌  Binance API error: {exc.message}\n")
        logger.error("Market order FAILED | %s", exc)
        return {"success": False, "error": str(exc)}

    except (ConnectionError, TimeoutError) as exc:
        print(f"  ❌  Network error: {exc}\n")
        logger.error("Market order network error | %s", exc)
        return {"success": False, "error": str(exc)}


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: str,
    price: str,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """
    Place a LIMIT order.

    The order will rest on the book until the market reaches `price`
    or the order is cancelled (GTC = Good Till Cancel).
    """
    _print_order_request(symbol, side, "LIMIT", quantity, price=price)

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce=time_in_force,
        )
        _print_order_response(response)
        print("  ✅  Limit order placed successfully!\n")
        logger.info(
            "Limit order SUCCESS | orderId=%s status=%s price=%s",
            response.get("orderId"),
            response.get("status"),
            response.get("price"),
        )
        return {"success": True, "response": response}

    except BinanceAPIError as exc:
        print(f"  ❌  Binance API error: {exc.message}\n")
        logger.error("Limit order FAILED | %s", exc)
        return {"success": False, "error": str(exc)}

    except (ConnectionError, TimeoutError) as exc:
        print(f"  ❌  Network error: {exc}\n")
        logger.error("Limit order network error | %s", exc)
        return {"success": False, "error": str(exc)}


def place_stop_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: str,
    stop_price: str,
) -> Dict[str, Any]:
    """
    BONUS: Place a STOP_MARKET order.

    The order triggers a market order when `stop_price` is reached.
    Commonly used as a stop-loss.
    """
    _print_order_request(symbol, side, "STOP_MARKET", quantity, stop_price=stop_price)

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            type="STOP_MARKET",
            quantity=quantity,
            stopPrice=stop_price,
        )
        _print_order_response(response)
        print("  ✅  Stop-Market order placed successfully!\n")
        logger.info(
            "Stop-Market order SUCCESS | orderId=%s status=%s stopPrice=%s",
            response.get("orderId"),
            response.get("status"),
            stop_price,
        )
        return {"success": True, "response": response}

    except BinanceAPIError as exc:
        print(f"  ❌  Binance API error: {exc.message}\n")
        logger.error("Stop-Market order FAILED | %s", exc)
        return {"success": False, "error": str(exc)}

    except (ConnectionError, TimeoutError) as exc:
        print(f"  ❌  Network error: {exc}\n")
        logger.error("Stop-Market order network error | %s", exc)
        return {"success": False, "error": str(exc)}
