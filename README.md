# 🤖 Binance Futures Testnet – Trading Bot

A clean, production-style Python CLI application that places **Market**, **Limit**, and **Stop-Market** orders on the **Binance USDT-M Futures Testnet**.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API client (signing, HTTP, error handling)
│   ├── orders.py          # Order placement logic + formatted output
│   ├── validators.py      # Pure input validation helpers
│   └── logging_config.py  # Rotating file + console logging setup
├── logs/
│   └── trading_bot.log    # Auto-created on first run
├── cli.py                 # CLI entry point (argparse + interactive mode)
├── .env.example           # Template for API credentials
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet API Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in (or register with GitHub)
3. Navigate to **Account → API Key** and generate a key pair
4. Copy your **API Key** and **Secret Key**

### 2. Clone & Install

```bash
git clone <your-repo-url>
cd trading_bot

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
cp .env.example .env
# Open .env and fill in your testnet API key and secret
```

`.env` contents:
```
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

---

## How to Run

### Option A – Direct Flags (scriptable)

```bash
# Market BUY
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Market SELL
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001

# Limit BUY (price below market to rest on book)
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 50000

# Limit SELL
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 4000

# Stop-Market (bonus order type) – triggers market order when price hits stop
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 58000
```

### Option B – Interactive Mode (guided prompts)

```bash
python cli.py --interactive
```

You'll be walked through each field with real-time validation and a confirmation step before the order is sent.

### Help

```bash
python cli.py --help
```

---

## Sample Output

```
╔══════════════════════════════════════════════════════════╗
║        Binance Futures Testnet  –  Trading Bot           ║
║                     USDT-M                               ║
╚══════════════════════════════════════════════════════════╝

────────────────────────────────────────────────────────────
  📤  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
────────────────────────────────────────────────────────────
────────────────────────────────────────────────────────────
  📥  ORDER RESPONSE
────────────────────────────────────────────────────────────
  Order ID     : 3928401029
  Client OID   : web_abc123
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Status       : FILLED
  Orig Qty     : 0.001
  Executed Qty : 0.001
  Avg Price    : 62345.10
  Timestamp    : 2025-01-15 10:23:44 UTC
────────────────────────────────────────────────────────────
  ✅  Market order placed successfully!
```

---

## Logging

All activity is written to `logs/trading_bot.log`:

- **DEBUG** level: full request parameters and raw API responses
- **INFO** level: order placement events and outcomes
- **ERROR** level: API errors, validation failures, network issues

Log rotation: 5 MB per file, 3 backups kept.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing API credentials | Exits with clear message |
| Invalid CLI input | Prints validation error, exits cleanly |
| Binance API error (e.g. bad qty) | Prints error code + message, logs full details |
| Network / timeout | Catches exception, prints user-friendly message |
| Unknown order type | Caught at validation layer |

---

## Assumptions

- All orders use the **Binance USDT-M Futures Testnet** (`https://testnet.binancefuture.com`)
- Limit orders default to `timeInForce=GTC` (Good Till Cancel)
- Quantity precision is passed as-is — Binance enforces symbol-specific `LOT_SIZE` filters on testnet
- No leverage or margin settings are modified by this bot; the account's existing leverage applies
- Credentials are loaded from `.env` (via `python-dotenv`) or pre-set environment variables

---

## Bonus Features Implemented

- ✅ **Stop-Market order type** (third order type beyond Market + Limit)
- ✅ **Enhanced interactive CLI** with guided prompts, per-field validation, and confirmation step

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP client for REST API calls |
| `python-dotenv` | Load credentials from `.env` file |

No Binance SDK used — all API communication is via raw REST calls with HMAC-SHA256 signing.
