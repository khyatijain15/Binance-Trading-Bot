# 🤖 Binance Futures Testnet Trading Bot

A professional, interview-ready Python application for placing orders on the **Binance USDT-M Futures Testnet**. Features both a **CLI interface** and a **Web Dashboard UI**, built with clean architecture, robust validation, comprehensive logging, and graceful error handling.

---

## ✨ Features

| Feature | Description |
|---|---|
| **MARKET Orders** | Place instant market orders on USDT-M Futures |
| **LIMIT Orders** | Place limit orders with GTC (Good-Till-Cancelled) time-in-force |
| **STOP-LIMIT Orders** | Place conditional stop-limit orders with a trigger price |
| **Web Dashboard** | Beautiful black & white themed web UI with animations |
| **CLI Interface** | Colourful terminal interface with box-drawing and status badges |
| **Input Validation** | Every parameter is validated before reaching the API |
| **Custom Exceptions** | `ValidationError`, `APIError`, `NetworkError` hierarchy |
| **Rotating Logs** | Structured, rotating file logs in `logs/trading.log` |
| **Secure Credentials** | API keys loaded from `.env` — never hardcoded |
| **Type Hints & Docstrings** | Full PEP 484 annotations and Google-style docstrings |

---

## 📂 Project Structure

```
trading_bot/
│
├── bot/                         # Core trading bot package (the backend)
│   ├── __init__.py              # Package init with exception re-exports
│   ├── client.py                # Binance API client wrapper
│   ├── orders.py                # High-level order placement logic
│   ├── validators.py            # Input validation functions
│   ├── logging_config.py        # Centralised rotating-file logger
│   └── exceptions.py            # Custom exception hierarchy
│
├── templates/
│   └── index.html               # Web dashboard UI (single-page app)
│
├── logs/
│   └── trading.log              # Auto-generated at runtime
│
├── .env.example                 # Template for environment variables
├── .env                         # Your actual API keys (DO NOT commit)
├── .gitignore                   # Files excluded from version control
├── app.py                       # Flask web UI server
├── cli.py                       # CLI entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🚀 Complete Setup Guide (Step by Step)

### Step 1 — Clone the Repository

```bash
git clone <repository-url>
cd trading_bot
```

### Step 2 — Create a Python Virtual Environment

```bash
python3 -m venv venv
```

### Step 3 — Activate the Virtual Environment

```bash
# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

> ✅ You'll see `(venv)` appear at the start of your terminal prompt when it's active.

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `python-binance` — Binance API wrapper
- `python-dotenv` — Load `.env` file automatically
- `requests` — HTTP library
- `flask` — Web framework for the dashboard UI

### Step 5 — Get Binance Futures Testnet API Keys

1. Open **https://testnet.binancefuture.com** in your browser
2. Click **Log In** → sign in with your **GitHub** account
3. Click your profile icon (top-right) → **API Management**
4. Click **Create API** → give it a name (e.g. `trading-bot`)
5. Copy both the **API Key** and **Secret Key**

> ⚠️ **Important**: The Spot testnet (`testnet.binance.vision`) and Futures testnet (`testnet.binancefuture.com`) use **completely different** API keys. Make sure you get yours from the **Futures** testnet.

### Step 6 — Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` in any editor and paste your credentials:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> 🔒 The `.gitignore` is already configured to exclude `.env` from version control.

### Step 7 — You're Ready!

You can now use either the **CLI** or the **Web UI**. See the sections below.

---

## 💻 CLI Usage — All Commands

> **Important**: Always activate the virtual environment first:
> ```bash
> source venv/bin/activate
> ```

### Buy BTCUSDT at Market Price

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Sell BTCUSDT at Market Price

```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### Buy ETHUSDT at a Limit Price

```bash
python cli.py --symbol ETHUSDT --side BUY --type LIMIT --quantity 0.01 --price 3500
```

### Sell BTCUSDT at a Limit Price

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
```

### Buy BTCUSDT with Stop-Limit (Bonus Feature)

This order will become an active LIMIT order when the market price drops to the stop price:

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --type STOP_LIMIT \
  --quantity 0.001 \
  --price 95000 \
  --stop-price 94500
```

### Sell ETHUSDT with Stop-Limit

```bash
python cli.py \
  --symbol ETHUSDT \
  --side SELL \
  --type STOP_LIMIT \
  --quantity 0.01 \
  --price 4000 \
  --stop-price 4100
```

### View Help

```bash
python cli.py --help
```

Output:
```
usage: cli.py [-h] --symbol SYMBOL --side {BUY,SELL}
              --type {MARKET,LIMIT,STOP_LIMIT} --quantity QUANTITY
              [--price PRICE] [--stop-price STOP_PRICE]

Binance Futures Testnet Trading Bot – Place orders via CLI.

options:
  -h, --help            show this help message and exit
  --symbol SYMBOL       Trading pair symbol (e.g. BTCUSDT).
  --side {BUY,SELL}     Order side: BUY or SELL.
  --type {MARKET,LIMIT,STOP_LIMIT}
                        Order type: MARKET, LIMIT, or STOP_LIMIT.
  --quantity QUANTITY   Order quantity (must be > 0).
  --price PRICE         Limit price (required for LIMIT and STOP_LIMIT orders).
  --stop-price STOP_PRICE
                        Stop (trigger) price (required for STOP_LIMIT orders).
```

### CLI Arguments Reference

| Argument | Required | Description | Example |
|---|---|---|---|
| `--symbol` | ✅ Yes | Trading pair symbol | `BTCUSDT`, `ETHUSDT` |
| `--side` | ✅ Yes | Order side | `BUY` or `SELL` |
| `--type` | ✅ Yes | Order type | `MARKET`, `LIMIT`, or `STOP_LIMIT` |
| `--quantity` | ✅ Yes | Trade quantity (must be > 0) | `0.001` |
| `--price` | For LIMIT/STOP_LIMIT | Limit price | `95000` |
| `--stop-price` | For STOP_LIMIT only | Stop (trigger) price | `94500` |

---

## 🌐 Web Dashboard UI

The project includes a beautiful **black & white themed** web dashboard as an alternative to the CLI.

### Start the Web UI

```bash
source venv/bin/activate
python app.py
```

Then open **http://localhost:5050** in your browser.

### Web UI Features

- **Order Form** — Select symbol, side (BUY/SELL), type, quantity, price
- **Live Response Panel** — See order results instantly
- **Session Order History** — Track all orders placed in the current session
- **Live Log Viewer** — View `logs/trading.log` entries in real-time
- **Animations** — Smooth fade-ins, slide-ups, and hover effects
- **Toast Notifications** — Success/error popups for every action

> 💡 The web UI uses the **same** `bot/` package as the CLI. There's no separate backend — `bot/client.py`, `bot/orders.py`, and `bot/validators.py` are shared.

---

## 📊 Sample CLI Output

### Successful MARKET Order

```
  ╔╗ ╦╔╗╔╔═╗╔╗╔╔═╗╔═╗  ╔╗ ╔═╗╔╦╗
  ╠╩╗║║║║╠═╣║║║║  ║╣   ╠╩╗║ ║ ║
  ╚═╝╩╝╚╝╩ ╩╝╚╝╚═╝╚═╝  ╚═╝╚═╝ ╩
  ────────────────────────────────────────
  Futures Testnet Trading Bot  •  2026-06-08 14:17:44

╔════════════════════════════════════════════════════╗
║  📋  ORDER REQUEST                                 ║
╠════════════════════════════════════════════════════╣
║  Symbol       BTCUSDT                              ║
║  Side         ▲ BUY                                ║
║  Type         MARKET                               ║
║  Quantity     0.001                                ║
╚════════════════════════════════════════════════════╝

  ⏳ Connecting to Binance Futures Testnet...

╔════════════════════════════════════════════════════╗
║  📊  ORDER RESPONSE                                ║
╠════════════════════════════════════════════════════╣
║  Order ID     14487540161                          ║
║  Symbol       BTCUSDT                              ║
║  Side         ▲ BUY                                ║
║  Type         MARKET                               ║
║  Status       NEW                                  ║
╠════════════════════════════════════════════════════╣
║  Exec. Qty    0.0010                               ║
║  Avg. Price   0.00000000                           ║
╚════════════════════════════════════════════════════╝

  ✅ SUCCESS — Order placed successfully.
```

### Validation Error (Missing Price for LIMIT)

```
╔════════════════════════════════════════════════════╗
║  ❌  ORDER FAILED                                  ║
╠════════════════════════════════════════════════════╣
║  LIMIT orders require a price greater than 0.      ║
╚════════════════════════════════════════════════════╝
```

---

## 📝 Logging

All events are logged to `logs/trading.log` with rotation (5 MB max, 3 backups).

### Log Format

```
timestamp | level | module | message
```

### What Is Logged

| Event | Log Level |
|---|---|
| Order requests & responses | `INFO` |
| Validation passed | `DEBUG` |
| Validation failures | `WARNING` |
| Binance API errors (with error codes) | `ERROR` |
| Network / timeout errors | `ERROR` |
| Unexpected exceptions (with stack trace) | `CRITICAL` |

### Sample Log Entries

```
2026-06-08 14:17:44 | INFO     | bot.client           | Binance Futures Testnet client initialised.
2026-06-08 14:17:44 | INFO     | bot.orders           | Dispatching MARKET order – BUY 0.001 BTCUSDT
2026-06-08 14:17:44 | INFO     | bot.client           | Placing MARKET order: symbol=BTCUSDT side=BUY qty=0.001
2026-06-08 14:17:45 | INFO     | cli                  | Order placed: {'order_id': 14487540161, ...}
2026-06-08 14:18:01 | INFO     | bot.orders           | Dispatching LIMIT order – SELL 0.001 BTCUSDT @ 95000.0
2026-06-08 14:18:01 | INFO     | bot.client           | Placing LIMIT order: symbol=BTCUSDT side=SELL qty=0.001 price=95000.0
2026-06-08 14:18:01 | INFO     | cli                  | Order placed: {'order_id': 14487858025, ...}
2026-06-08 14:27:28 | WARNING  | bot.validators       | Validation failed: Quantity must be greater than 0. Got: -5.0
```

---

## 🛡️ Error Handling

The bot **never** exposes raw stack traces to users. Every error is caught and displayed cleanly:

| Scenario | What Happens |
|---|---|
| Empty symbol | `ValidationError` → "Symbol must not be empty." |
| Invalid side (e.g. `HOLD`) | Rejected by argparse with choices error |
| Quantity ≤ 0 | `ValidationError` → "Quantity must be greater than 0." |
| Missing price for LIMIT | `ValidationError` → "LIMIT orders require a price greater than 0." |
| Missing stop-price for STOP_LIMIT | `ValidationError` → "STOP_LIMIT orders require a --stop-price greater than 0." |
| Invalid/expired API keys | `APIError` → "[Binance -2015] Invalid API-key..." |
| Invalid symbol on exchange | `APIError` → Binance error code and message |
| No internet / DNS failure | `NetworkError` → "Network error while contacting Binance" |
| Request timeout | `NetworkError` → timeout description |
| Any other unexpected error | Generic message + full stack trace saved to `logs/trading.log` |

---

## 🏗️ Architecture & Design Decisions

```
┌──────────────┐     ┌───────────────┐
│   cli.py     │     │   app.py      │
│  (Terminal)  │     │  (Flask Web)  │
└──────┬───────┘     └──────┬────────┘
       │                    │
       └────────┬───────────┘
                │
       ┌────────▼────────┐
       │   bot/orders.py  │   ← Orchestration layer
       └────────┬────────┘
                │
       ┌────────▼──────────┐
       │ bot/validators.py │   ← Input validation
       └────────┬──────────┘
                │
       ┌────────▼────────┐
       │  bot/client.py   │   ← Binance API wrapper
       └────────┬────────┘
                │
       ┌────────▼─────────────────────┐
       │  Binance Futures Testnet API  │
       └───────────────────────────────┘
```

- **Separation of Concerns** — CLI parsing, web routing, validation, client communication, and order logic live in separate modules.
- **Shared Backend** — Both `cli.py` and `app.py` import from the same `bot/` package. No code duplication.
- **Custom Exception Hierarchy** — A common `TradingBotError` base class allows fine-grained or broad `except` clauses.
- **Normalised Responses** — The client wrapper converts raw Binance JSON into a flat, predictable dict.
- **Fail Fast** — Inputs are validated *before* any network call, saving latency on bad data.
- **No Hardcoded Credentials** — All secrets loaded from `.env` via `python-dotenv`.

---

## 🧩 Assumptions

1. The user has a valid **Binance Futures Testnet** API key pair (from `testnet.binancefuture.com`).
2. Python **3.11+** is installed.
3. The testnet account has sufficient virtual funds for the requested trades.
4. Symbol precision requirements match the testnet's exchange info (e.g. `BTCUSDT` minimum order size).
5. Only **isolated margin** mode is assumed (no cross-margin configuration).
6. The default time-in-force for LIMIT orders is **GTC** (Good-Till-Cancelled).

---

## 🔮 Future Improvements

- [ ] **OCO (One-Cancels-Other) orders** — support additional complex order types
- [ ] **Exchange info cache** — fetch and cache symbol rules to validate precision before order submission
- [ ] **Retry logic** — exponential back-off on transient network failures
- [ ] **Async support** — migrate to `python-binance` async client for high-throughput bots
- [ ] **Unit & integration tests** — pytest suite with mocked API responses
- [ ] **Docker support** — `Dockerfile` for reproducible deployments
- [ ] **Configuration file** — YAML/TOML config for default symbols, quantities, and logging levels
- [ ] **Webhook / Telegram alerts** — notify on order fills or failures
- [ ] **WebSocket price feed** — live price ticker in the web dashboard
- [ ] **Position tracking** — display open positions and PnL

---
