# Binance Futures Testnet CLI

A small Python command-line tool for placing **Market**, **Limit** and **Stop-Market** orders on the **Binance USDT-M Futures Testnet**. It signs requests itself (HMAC-SHA256, no Binance SDK), validates input before sending anything, and logs every request and response.

> **Testnet only.** The API base URL is hardcoded to `https://testnet.binancefuture.com`, so no real funds are involved. This is an educational project, not financial advice, and it implements **no trading strategy**: it places the orders you ask it to place. Never put real (mainnet) API keys in it.

## Project structure

```
.
├── bot/
│   ├── client.py          # REST client: request signing, HTTP calls, error handling
│   ├── orders.py          # order placement logic and formatted output
│   ├── validators.py      # input validation helpers
│   └── logging_config.py  # rotating file and console logging
├── tests/                 # pytest tests for the validators
├── cli.py                 # entry point (flags or interactive mode)
├── .env.example           # template for credentials
└── requirements.txt
```

## Setup

1. Create testnet API keys at [testnet.binancefuture.com](https://testnet.binancefuture.com) (Account, then API Key).
2. Install:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your testnet key and secret
```

`.env` is listed in `.gitignore`. Never commit it.

## Usage

```bash
# Market order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit order (price below market so it rests on the book)
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000

# Stop-Market order
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 58000

# Guided prompts with a confirmation step
python cli.py --interactive
```

Run `python cli.py --help` for all options.

## Example output

The values below are illustrative, not taken from a real run.

```
  ORDER REQUEST SUMMARY
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001

  ORDER RESPONSE
  Order ID     : 3928401029
  Status       : FILLED
  Executed Qty : 0.001
  Avg Price    : 62345.10
```

## Logging

Activity is written to `logs/trading_bot.log` (rotating, 5 MB per file, 3 backups): request parameters and raw responses at DEBUG, order events at INFO, API, validation and network errors at ERROR. Signatures are not written to the log.

## Error handling

| Scenario | Behaviour |
|---|---|
| Missing API credentials | Exits with a clear message |
| Invalid CLI input | Prints the validation error and exits |
| Binance API error (for example a bad quantity) | Prints the error code and message, logs the details |
| Network error or timeout | Catches it and prints a readable message |

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The tests cover the input validators only. The API client and order flow are not covered by automated tests, and nothing here has been run against a live exchange.

## Notes and limitations

- Limit orders use `timeInForce=GTC`. Quantity precision is passed as entered, and Binance enforces each symbol's lot-size rules.
- Leverage and margin settings are not changed; the account's existing settings apply.
- Credentials are read from `.env` or the environment.
- Dependencies: `requests` and `python-dotenv`.

## License

MIT, see [LICENSE](LICENSE).
