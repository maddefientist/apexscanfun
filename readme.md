# SPL Token Charting Telegram Bot (Solana DEX Analysis)

This Python Telegram bot allows users to analyze Solana-based SPL tokens via the `/chart <token_address>` command. It fetches real-time and historical price data from DEX APIs like GeckoTerminal, generates charts with key indicators (e.g., RSI, MACD, Support/Resistance), and returns the results directly in Telegram. Built to scale with future web app integration and alerting capabilities.

---

## ⚙️ Features (MVP)

- `/chart <token_address>` — returns price chart with indicators
- Real-time and historical DEX data (via GeckoTerminal)
- Chart includes candlesticks, RSI, support/resistance
- `/legend` — explains the indicators and patterns
- Modular architecture (Telegram first, web-ready backend)

---

## 🧰 Tech Stack

- **Language**: Python 3.10+
- **Telegram Bot**: [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot)
- **Charting**: `matplotlib`, `mplfinance`
- **Indicators**: `pandas`, `ta` (technical analysis lib)
- **HTTP**: `requests` or `httpx`
- **Environment**: `.env` + `python-dotenv`

---

## 📁 Project Structure

splbot/ │ ├── bot.py # Telegram command handlers ├── charting.py # Chart + indicator generation ├── data_fetcher.py # DEX API integration (e.g. GeckoTerminal) ├── indicators.py # RSI, MACD, etc. ├── support_resistance.py # Price level detection ├── legend.py # Static help text ├── config.py # Env loading and constants ├── requirements.txt └── .env # TELEGRAM_TOKEN, API keys, etc.

yaml
Copy
Edit

---

## 🚀 Setup Instructions

### 1. Clone + Install

```bash
git clone https://github.com/yourname/splbot.git
cd splbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
2. .env File (create in root)
env
Copy
Edit
TELEGRAM_TOKEN=your_telegram_bot_token_here
GECKO_API_BASE=https://api.geckoterminal.com/api/v2
3. Run the Bot
bash
Copy
Edit
python bot.py
Bot will use long polling and respond to:

bash
Copy
Edit
/chart <token_address>
/legend
✅ Sample Command
plaintext
Copy
Edit
/chart 9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E  # (example: USDC)
🔜 Coming Soon
Alert system for RSI, price levels

Enhanced pattern recognition (double tops, triangles)

Inline buttons + timeframes

Web dashboard integration

📦 Example requirements.txt
Copy
Edit
python-telegram-bot==20.7
matplotlib
mplfinance
pandas
ta
requests
python-dotenv
🧠 Notes
GeckoTerminal API: Docs

Support/resistance is calculated using peak/trough clustering

SPL token addresses should be provided as base58 strings

Token metadata (e.g., symbol) can be resolved via Solana token list

🔐 Security
Do not expose your bot token.

Use .env to manage secrets and python-dotenv to load them.

🧪 Dev Tips
Use logging for debug messages in bot handlers

Wrap API calls in try/except to gracefully handle token errors

Add @restricted decorator if limiting access to yourself during dev

