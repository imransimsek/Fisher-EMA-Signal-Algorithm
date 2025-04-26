import pandas as pd
import numpy as np
import logging
from binance.client import Client
from datetime import datetime, timedelta
import config
import os
from telegram_sender import send_error_message

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('binance_client')

# Binance istemcisi oluşturulması
try:
    # API anahtarlarını doğrudan çekelim
    api_key = os.environ.get("BINANCE_API_KEY", "")
    api_secret = os.environ.get("BINANCE_API_SECRET", "")
    
    if not api_key or not api_secret:
        error_msg = f"Binance API anahtarları eksik veya boş! KEY={bool(api_key)}, SECRET={bool(api_secret)}"
        logger.error(error_msg)
        client = None
    else:
        logger.info(f"API anahtarlarıyla Binance istemcisi oluşturuluyor. KEY uzunluğu: {len(api_key)}")
        client = Client(api_key, api_secret)
        logger.info("Binance istemcisi başarıyla oluşturuldu")
except Exception as e:
    error_msg = f"Binance istemcisi oluşturulurken hata: {e}"
    logger.error(error_msg)
    client = None

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
    try:
        if client is None:
            logger.error("Binance client oluşturulmamış! API anahtarlarını kontrol edin.")
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
        logger.error(f"Veri çekerken hata: {e}")
        return pd.DataFrame()
