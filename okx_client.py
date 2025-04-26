import pandas as pd
import requests
import logging
import time
from datetime import datetime
import config
from telegram_sender import send_error_message

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('okx_client')

def fetch_klines(symbol: str, interval: str, limit: int = 100) -> pd.DataFrame:
    """
    OKX'den belirli bir sembol ve zaman dilimi için kline verilerini çeker
    
    Args:
        symbol: İşlem çifti (örn: BTC-USDT)
        interval: Zaman dilimi (örn: 5m, 15m, 30m, 1H)
        limit: Çekilecek maksimum kline sayısı
        
    Returns:
        Pandas DataFrame içeren OHLCV verileri
    """
    try:
        logger.info(f"{symbol} için {interval} verisi çekiliyor...")
        
        # OKX API endpoint
        url = "https://www.okx.com/api/v5/market/candles"
        
        # API parametreleri
        params = {
            'instId': symbol,
            'bar': interval,
            'limit': str(limit)
        }
        
        # İstek gönder
        response = requests.get(url, params=params)
        result = response.json()
        
        if result.get('code') != '0':
            error_msg = f"OKX API Hatası: {result.get('msg', 'Bilinmeyen hata')}"
            logger.error(error_msg)
            send_error_message(error_msg, "OKX API", f"Kod: {result.get('code')}")
            return pd.DataFrame()
        
        # Veri var mı kontrol et
        data = result.get('data', [])
        if not data:
            error_msg = f"OKX'den veri alınamadı: {symbol} {interval}"
            logger.error(error_msg)
            return pd.DataFrame()
        
        # DataFrame oluştur
        # OKX verileri şu sırada: [timestamp, open, high, low, close, vol, volCcy, ...]
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if len(data[0]) > 6:
            extra_columns = [f'extra_{i}' for i in range(len(data[0]) - 6)]
            columns.extend(extra_columns)
        
        df = pd.DataFrame(data, columns=columns)
        
        # Veri tiplerini düzelt
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        # OKX verileri ters sıralanmış olabilir (en yeni veri ilk), standart hale getir
        df = df.sort_values('timestamp')
        
        # İndeksi zaman damgası olarak ayarla
        df.set_index('timestamp', inplace=True)
        
        logger.info(f"{symbol} {interval} için {len(df)} kline verisi çekildi")
        return df
    
    except Exception as e:
        error_msg = f"Veri çekerken hata: {e}"
        logger.error(error_msg)
        try:
            send_error_message(error_msg, "Veri Çekme", f"{symbol} {interval}: {str(e)}")
        except:
            pass
        return pd.DataFrame()
