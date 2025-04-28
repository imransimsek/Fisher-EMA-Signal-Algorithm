import pandas as pd
import logging
from typing import Dict, Any, List, Tuple

# Log settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('signal_detector')

def detect_signals(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detects signals from Fisher + EMA Band indicator
    
    New Signal Logic:
    1. AŞIRI_ALIM: Trigger, above upper band
    2. AŞIRI_SATIM: Trigger, below lower band
    """
    signals = []
    
    # Get last data point
    if len(df) < 1:
        logger.warning("At least 1 data point is required for signal detection")
        return signals
    
    current = df.iloc[-1]  # Last row
    
    # Signal 1: Trigger, above upper band (EXTREME_BUY)
    if current['trigger'] > current['upper_band']:
        signal = {
            'type': 'EXTREME_BUY',
            'strength': 'WARNING',
            'price': current['close'],
            'trigger': current['trigger'],
            'band': current['upper_band'],
            'fisher': current['fisher'],
            'time': current.name,  # index value (timestamp)
            'description': 'Trigger, above upper band! Extreme buy zone.'
        }
        signals.append(signal)
        logger.info(f"Extreme Buy Signal Detected: Trigger={current['trigger']:.4f}, Upper Band={current['upper_band']:.4f}")
    
    # Signal 2: Trigger, below lower band (EXTREME_SELL)
    elif current['trigger'] < current['lower_band']:
        signal = {
            'type': 'EXTREME_SELL',
            'strength': 'WARNING',
            'price': current['close'],
            'trigger': current['trigger'],
            'band': current['lower_band'],
            'fisher': current['fisher'],
            'time': current.name,
            'description': 'Trigger, below lower band! Extreme sell zone.'
        }
        signals.append(signal)
        logger.info(f"Extreme Sell Signal Detected: Trigger={current['trigger']:.4f}, Lower Band={current['lower_band']:.4f}")
    
    return signals
