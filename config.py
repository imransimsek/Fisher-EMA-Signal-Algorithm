import os
from dotenv import load_dotenv

# .env dosyasından ortam değişkenlerini yükle
load_dotenv()

# Binance API ayarları
BINANCE_API_KEY = "qXcKqSvRoExKay13MPcQedAQKd1NiqJYKVSeOQdoIDztmq9MCO5FxiWJPRJ3pbCa"
BINANCE_API_SECRET = "TnUJcH5jTvXcgZy1AG2l3RIvPerp1yrScdfcAkKVH3f8lxpXlQNIhoKhFsuOF8iw"

# Telegram ayarları
TELEGRAM_BOT_TOKEN = "7288825391:AAFzbPiVIswOpzZoWsuaPE8cFETUx2N10YU"
TELEGRAM_CHAT_ID = "926499549"

# Semboller ve zaman dilimleri
SYMBOLS = ["BTCUSDT", "ETHUSDT","SOLUSDT","AVAXUSDT"]
INTERVALS = ["5m", "15m"]

# İndikatör parametreleri
FISHER_LENGTH = 10
EMA_LENGTH = 5
RANGE_OFFSET = 1.0

# Debug modu
DEBUG = False
