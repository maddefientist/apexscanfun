import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set")

# GeckoTerminal API Base URL
GECKO_API_BASE = os.getenv("GECKO_API_BASE", "https://api.geckoterminal.com/api/v2")

# Timeframes available for charts
# The API supports 'minute', 'hour', 'day' with an aggregate parameter
TIMEFRAMES = {
    "1h": {"name": "1 Hour", "endpoint": "hour", "aggregate": 1},
    "4h": {"name": "4 Hours", "endpoint": "hour", "aggregate": 4},
    "1d": {"name": "1 Day", "endpoint": "day", "aggregate": 1},
    "1w": {"name": "1 Week", "endpoint": "day", "aggregate": 7}
}

# Default timeframe
DEFAULT_TIMEFRAME = "1h"

# Chart settings
CHART_SETTINGS = {
    "window_size": 100,  # Number of candles to show (increased from 50)
    "support_resistance_window": 5,  # Window for support/resistance detection
    "support_resistance_threshold": 0.02,  # Threshold for support/resistance clustering
}

# File paths
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

# Solana token list URL (for future use to get token metadata)
SOLANA_TOKEN_LIST_URL = "https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/solana.tokenlist.json"