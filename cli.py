"""
cli.py
------
CLI entry point for the Binance Futures Testnet Trading Bot.

Two modes:
  1. Direct flags  (scriptable / CI-friendly)
     python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  2. Interactive mode (--interactive)
     python cli.py --interactive
     Walks the user through prompts with validation at each step.

Environment variables (or .env file):
  BINANCE_API_KEY    – your testnet API key
  BINANCE_API_SECRET – your testnet API secret
"""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

from bot.logging_config import setup_logging
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)
from bot.client import BinanceFuturesClient
from bot.orders import (
    place_market_order,
    place_limit_order,
    place_stop_market_order,
)

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════════════════════╗
║        Binance Futures Testnet  –  Trading Bot           ║
║                     USDT-M                               ║
╚══════════════════════════════════════════════════════════╝
"""


# ── Credential loader ────────────────────────────────────────────────────────

def load_credentials() -> tuple[str, str]:
    """Load API key and secret from environment / .env file."""
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print("\n  ⚠️  API credentials not found in environment.")
        print("  Set BINANCE_API_KEY and BINANCE_API_SECRET in a .env file or")
        print("  export them as environment variables.\n")
        logger.error("Missing API credentials. Exiting.")
        sys.exit(1)

    return api_key, api_secret


# ── Interactive mode ─────────────────────────────────────────────────────────

def _prompt(prompt_text: str, validator, *validator_args) -> str:
    """Keep prompting until the validator passes. Returns validated value."""
    while True:
        raw = input(prompt_text).strip()
        try:
            return validator(raw, *validator_args)
        except ValueError as exc:
            print(f"  ⚠️  {exc}  – please try again.")


def interactive_mode(client: BinanceFuturesClient) -> None:
    """Guided interactive order placement."""
    print(BANNER)
    print("  Welcome to interactive order placement.\n")

    # ── Gather inputs ──────────────────────────────────────────────────────
    symbol = _prompt("  Symbol (e.g. BTCUSDT): ", validate_symbol)
    side   = _prompt("  Side   [BUY / SELL]  : ", validate_side)

    print("  Order types: MARKET | LIMIT | STOP_MARKET")
    order_type = _prompt("  Order type           : ", validate_order_type)

    quantity = _prompt("  Quantity             : ", validate_quantity)

    price = None
    stop_price = None

    if order_type == "LIMIT":
        price = _prompt("  Limit price          : ", validate_price, order_type)

    if order_type == "STOP_MARKET":
        stop_price = _prompt("  Stop price           : ", validate_stop_price, order_type)

    # ── Confirm ────────────────────────────────────────────────────────────
    print()
    print("  ─── Confirm Order ───────────────────────────────────────")
    print(f"  {side} {quantity} {symbol} @ {order_type}", end="")
    if price:
        print(f" price={price}", end="")
    if stop_price:
        print(f" stop={stop_price}", end="")
    print()

    confirm = input("\n  Proceed? [y/N]: ").strip().lower()
    if confirm != "y":
        print("  Order cancelled by user.\n")
        logger.info("User cancelled interactive order.")
        return

    # ── Place order ────────────────────────────────────────────────────────
    dispatch_order(client, symbol, side, order_type, quantity, price, stop_price)


# ── Order dispatcher ─────────────────────────────────────────────────────────

def dispatch_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price=None,
    stop_price=None,
) -> dict:
    """Route to the correct order function based on order_type."""
    logger.info(
        "Dispatching order | symbol=%s side=%s type=%s qty=%s",
        symbol, side, order_type, quantity,
    )

    if order_type == "MARKET":
        return place_market_order(client, symbol, side, quantity)

    elif order_type == "LIMIT":
        return place_limit_order(client, symbol, side, quantity, price)

    elif order_type == "STOP_MARKET":
        return place_stop_market_order(client, symbol, side, quantity, stop_price)

    else:
        # Should never reach here if validators ran
        raise ValueError(f"Unsupported order type: {order_type}")


# ── Argument parser ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet – CLI Trading Bot",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Market buy
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit sell
  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 2000

  # Stop-Market (bonus order type)
  python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 58000

  # Interactive mode (guided prompts)
  python cli.py --interactive
        """,
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Launch guided interactive order placement",
    )
    parser.add_argument("--symbol",     type=str, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       type=str, help="BUY or SELL")
    parser.add_argument("--type",       type=str, dest="order_type", help="MARKET | LIMIT | STOP_MARKET")
    parser.add_argument("--quantity",   type=str, help="Order quantity")
    parser.add_argument("--price",      type=str, default=None, help="Limit price (required for LIMIT)")
    parser.add_argument("--stop-price", type=str, default=None, dest="stop_price",
                        help="Stop trigger price (required for STOP_MARKET)")

    return parser


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    api_key, api_secret = load_credentials()
    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

    # ── Interactive mode ───────────────────────────────────────────────────
    if args.interactive:
        interactive_mode(client)
        return

    # ── Direct flag mode ───────────────────────────────────────────────────
    # All four core fields are required in flag mode
    required = ["symbol", "side", "order_type", "quantity"]
    missing = [r for r in required if not getattr(args, r)]
    if missing:
        formatted = ', '.join('--' + r.replace('_', '-') for r in missing)
        print(f"\n  ❌  Missing required arguments: {formatted}")
        print("  Run with --help for usage or --interactive for guided mode.\n")
        sys.exit(1)

    # Validate
    try:
        symbol     = validate_symbol(args.symbol)
        side       = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity   = validate_quantity(args.quantity)
        price      = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValueError as exc:
        print(f"\n  ❌  Validation error: {exc}\n")
        logger.error("Validation error: %s", exc)
        sys.exit(1)

    print(BANNER)
    dispatch_order(client, symbol, side, order_type, quantity, price, stop_price)


if __name__ == "__main__":
    main()
