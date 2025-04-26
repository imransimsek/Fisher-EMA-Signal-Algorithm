import os
import logging as logger
from dotenv import load_dotenv

# .env dosyasından ortam değişkenlerini yükle
load_dotenv()

# OKX API ayarları - artık yalnızca public API kullanıyoruz, anahtara gerek yok
# Private API'ye ihtiyaç duyarsanız, bu değişkenleri kullanın
OKX_API_KEY = os.environ.get("OKX_API_KEY", "")
OKX_API_SECRET = os.environ.get("OKX_API_SECRET", "")
OKX_API_PASSPHRASE = os.environ.get("OKX_API_PASSPHRASE", "")



# Telegram ayarları
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Semboller ve zaman dilimleri (OKX formatı)
SYMBOLS = os.environ.get("SYMBOLS", "BTC-USDT,ETH-USDT,SOL-USDT,AVAX-USDT").split(",")
INTERVALS = os.environ.get("INTERVALS", "5m,15m,30m,1H").split(",")

# İndikatör parametreleri
FISHER_LENGTH = int(os.environ.get("FISHER_LENGTH", "10"))
EMA_LENGTH = int(os.environ.get("EMA_LENGTH", "5"))
RANGE_OFFSET = float(os.environ.get("RANGE_OFFSET", "1.0"))

# Debug modu
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
