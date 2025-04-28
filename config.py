import os
import logging as logger
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# OKX API settings – now using only public API, no key required
# Use these variables if you need private API access
OKX_API_KEY = os.environ.get("OKX_API_KEY", "")
OKX_API_SECRET = os.environ.get("OKX_API_SECRET", "")
OKX_API_PASSPHRASE = os.environ.get("OKX_API_PASSPHRASE", "")



# Telegram settings
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Symbols and intervals (OKX format)
SYMBOLS = os.environ.get("SYMBOLS", "BTC-USDT,ETH-USDT,SOL-USDT,AVAX-USDT").split(",")
INTERVALS = os.environ.get("INTERVALS", "5m,15m,30m,1H").split(",")

# Fisher indicator parameters
FISHER_LENGTH = int(os.environ.get("FISHER_LENGTH", "10"))
EMA_LENGTH = int(os.environ.get("EMA_LENGTH", "5"))
RANGE_OFFSET = float(os.environ.get("RANGE_OFFSET", "1.0"))

# Debug mode
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
