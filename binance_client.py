import pandas as pd
import numpy as np
import logging
import os
from binance.client import Client
from datetime import datetime, timedelta
from telegram_sender import send_error_message

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('binance_client')

# Doğrudan ortam değişkenlerinden oku
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.environ.get("BINANCE_API_SECRET", "")

# Kontrol et ve logla
logger.info(f"BINANCE_API_KEY uzunluğu: {len(BINANCE_API_KEY)}")
logger.info(f"BINANCE_API_SECRET uzunluğu: {len(BINANCE_API_SECRET)}")

# Global client değişkeni
client = None

# Binance istemcisi oluştur
try:
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        error_msg = "Binance API anahtarları boş!"
        logger.error(error_msg)
        try:
            send_error_message(error_msg, "Binance API", "API anahtarları eksik veya boş")
        except:
            pass
    else:
        client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        logger.info("Binance istemcisi başarıyla oluşturuldu")
except Exception as e:
    error_msg = f"Binance istemcisi oluşturulurken hata: {e}"
    logger.error(error_msg)
    try:
        send_error_message(error_msg, "Binance Hata", str(e))
    except:
        pass

def fetch_klines(symbol: str, interval: str, limit: int = 500) -> pd.DataFrame:
    """
    Binance'dan belirli bir sembol ve zaman dilimi için kline verilerini çeker
    
    Args:
        symbol: İşlem çifti (örn: BTCUSDT)
        interval: Zaman dilimi (örn: 5m, 15m, 30m, 1h)
        limit: Çekilecek maksimum kline sayısı
        
    Returns:
        Pandas DataFrame içeren OHLCV verileri
    """
    global client
    
    try:
        if client is None:
            # Tekrar başlatmayı dene
            logger.info("İstemci yok, yeniden oluşturmayı deneyeceğim")
            try:
                client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
                logger.info("Binance istemcisi yeniden oluşturuldu")
            except Exception as e:
                error_msg = f"İstemci yeniden oluşturulamadı: {e}"
                logger.error(error_msg)
                return pd.DataFrame()
                
        logger.info(f"{symbol} için {interval} verisi çekiliyor...")
        
        # Verileri çek
        klines = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )
        
        # DataFrame oluştur
        data = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Veri tiplerini düzelt
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data['open'] = data['open'].astype(float)
        data['high'] = data['high'].astype(float)
        data['low'] = data['low'].astype(float)
        data['close'] = data['close'].astype(float)
        data['volume'] = data['volume'].astype(float)
        
        # İndeksi zaman damgası olarak ayarla
        data.set_index('timestamp', inplace=True)
        
        logger.info(f"{symbol} {interval} için {len(data)} kline verisi çekildi")
        return data
    
    except Exception as e:
        error_msg = f"Veri çekerken hata: {e}"
        logger.error(error_msg)
        try:
            send_error_message(error_msg, "Veri Çekme", f"{symbol} {interval}: {str(e)}")
        except:
            pass
        return pd.DataFrame()
