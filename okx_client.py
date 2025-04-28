import pandas as pd
import requests
import logging
import time
from datetime import datetime
import config
from telegram_sender import send_error_message

# Log settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('okx_client')

def fetch_klines(symbol: str, interval: str, limit: int = 100) -> pd.DataFrame:
    """
    Fetches kline data for a specific symbol and time interval from OKX
    
    Args:
        symbol: Trading pair (e.g., BTC-USDT)
        interval: Time interval (e.g., 5m, 15m, 30m, 1H)
        limit: Maximum number of klines to fetch
        
    Returns:
        Pandas DataFrame containing OHLCV data
    """
    try:
        logger.info(f"Fetching {interval} data for {symbol}...")
        
        # OKX API endpoint
        url = "https://www.okx.com/api/v5/market/candles"
        
        # API parameters
        params = {
            'instId': symbol,
            'bar': interval,
            'limit': str(limit)
        }
        
        # Send request
        response = requests.get(url, params=params)
        result = response.json()
        
        if result.get('code') != '0':
            error_msg = f"OKX API Error: {result.get('msg', 'Unknown error')}"
            logger.error(error_msg)
            send_error_message(error_msg, "OKX API", f"Code: {result.get('code')}")
            return pd.DataFrame()
        
        # Check if data is available
        data = result.get('data', [])
        if not data:
            error_msg = f"Failed to fetch data from OKX: {symbol} {interval}"
            logger.error(error_msg)
            return pd.DataFrame()
        
        # Create DataFrame
        # OKX data is in this order: [timestamp, open, high, low, close, vol, volCcy, ...]
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if len(data[0]) > 6:
            extra_columns = [f'extra_{i}' for i in range(len(data[0]) - 6)]
            columns.extend(extra_columns)
        
        df = pd.DataFrame(data, columns=columns)
        
        # Fix data types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        # OKX data might be reversed (newest data first), standardize
        df = df.sort_values('timestamp')
        
        # Set index to timestamp
        df.set_index('timestamp', inplace=True)
        
        logger.info(f"Fetched {len(df)} kline data for {symbol} {interval}")
        return df
    
    except Exception as e:
        error_msg = f"Error fetching data: {e}"
        logger.error(error_msg)
        try:
            send_error_message(error_msg, "Data Fetching", f"{symbol} {interval}: {str(e)}")
        except:
            pass
        return pd.DataFrame()
