import pandas as pd
import logging
from typing import Dict, Any, List, Tuple

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('signal_detector')

def detect_signals(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Fisher + EMA Band indikatöründen sinyal tespit eder
    
    Yeni Sinyal Mantığı:
    1. AŞIRI_ALIM: Trigger, üst bandın üstünde
    2. AŞIRI_SATIM: Trigger, alt bandın altında
    """
    signals = []
    
    # Son veriyi al
    if len(df) < 1:
        logger.warning("Sinyal tespiti için en az 1 veri noktası gerekiyor")
        return signals
    
    current = df.iloc[-1]  # En son satır
    
    # Sinyal 1: Trigger, üst bandın üzerinde (AŞIRI_ALIM)
    if current['trigger'] > current['upper_band']:
        signal = {
            'type': 'AŞIRI_ALIM',
            'strength': 'UYARI',
            'price': current['close'],
            'trigger': current['trigger'],
            'band': current['upper_band'],
            'fisher': current['fisher'],
            'time': current.name,  # index değeri (timestamp)
            'description': 'Trigger, üst bandın üzerine çıktı! Aşırı alım bölgesi.'
        }
        signals.append(signal)
        logger.info(f"AŞIRI ALIM sinyali tespit edildi: Trigger={current['trigger']:.4f}, Üst Band={current['upper_band']:.4f}")
    
    # Sinyal 2: Trigger, alt bandın altında (AŞIRI_SATIM)
    elif current['trigger'] < current['lower_band']:
        signal = {
            'type': 'AŞIRI_SATIM',
            'strength': 'UYARI',
            'price': current['close'],
            'trigger': current['trigger'],
            'band': current['lower_band'],
            'fisher': current['fisher'],
            'time': current.name,
            'description': 'Trigger, alt bandın altına indi! Aşırı satım bölgesi.'
        }
        signals.append(signal)
        logger.info(f"AŞIRI SATIM sinyali tespit edildi: Trigger={current['trigger']:.4f}, Alt Band={current['lower_band']:.4f}")
    
    return signals
