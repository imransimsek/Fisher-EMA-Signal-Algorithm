import os
from dotenv import load_dotenv

# .env dosyasından ortam değişkenlerini yükle
load_dotenv()

# Binance API ayarları
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET", "")

# Telegram ayarları
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Semboller ve zaman dilimleri
SYMBOLS = os.environ.get("SYMBOLS", "BTCUSDT,ETHUSDT,SOLUSDT,AVAXUSDT").split(",")
INTERVALS = os.environ.get("INTERVALS", "5m,15m").split(",")

# İndikatör parametreleri
FISHER_LENGTH = int(os.environ.get("FISHER_LENGTH", "21"))
EMA_LENGTH = int(os.environ.get("EMA_LENGTH", "89"))
RANGE_OFFSET = float(os.environ.get("RANGE_OFFSET", "2.5"))

# Debug modu
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
