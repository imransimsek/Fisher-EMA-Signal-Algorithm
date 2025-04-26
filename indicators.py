import numpy as np
import pandas as pd
import logging

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('indicators')

def fisher_ema_band(df: pd.DataFrame, length: int = 21, ema_length: int = 50, range_offset: float = 2.0) -> pd.DataFrame:
    """
    Pine Script Fisher Transform indikatörünü Python'a uyarlar
    
    Args:
        df: OHLC verilerini içeren DataFrame
        length: Fisher pencere uzunluğu
        ema_length: Fisher'ın EMA uzunluğu
        range_offset: Bantlar için aralık çarpanı
    
    Returns:
        İndikatör değerlerini içeren DataFrame
    """
    try:
        logger.debug(f"Fisher Transform hesaplanıyor: length={length}, ema_length={ema_length}, offset={range_offset}")
        
        # Kayıtları kopyala
        result_df = df.copy()
        
        # HL2 hesapla (High ve Low ortalaması)
        hl2 = (df['high'] + df['low']) / 2
        
        # Her period için en yüksek ve en düşük değerleri bul
        max_h = hl2.rolling(window=length).max()
        min_l = hl2.rolling(window=length).min()
        
        # nValue1 ve nFish için numpy dizileri oluştur
        nValue1 = np.zeros(len(df))
        nFish = np.zeros(len(df))
        
        # İlk length kadar satır için hesaplama yapamayız (yeterli veri yok)
        for i in range(length, len(df)):
            # Range 0 ise, varsayılan 0.5 değerini kullan
            if max_h[i] == min_l[i]:
                raw = 0.5
            else:
                # Value1 hesapla: normalize edilmiş hl2
                raw = (hl2[i] - min_l[i]) / (max_h[i] - min_l[i])
            
            # Pine Script'teki formülü uygula
            v1 = 0.33 * 2 * (raw - 0.5) + 0.67 * nValue1[i-1]
            
            # nValue2 sınırlarını kontrol et (-0.99 ile 0.99 arasında olmalı)
            if v1 > 0.99:
                v2 = 0.999
            elif v1 < -0.99:
                v2 = -0.999
            else:
                v2 = v1
            
            # nValue1'i güncelle
            nValue1[i] = v1
            
            # Fisher dönüşümünü uygula
            nFish[i] = 0.5 * np.log((1 + v2) / (1 - v2)) + 0.5 * nFish[i-1]
            
        # Pandas serisine dönüştür
        fisher = pd.Series(nFish, index=df.index)
        trigger = fisher.shift(1)  # Fisher 1 dönem geriye kaydırılmış hali
        
        # EMA hesapla
        ema_fish = fisher.ewm(span=ema_length, adjust=False).mean()
        
        # Üst ve alt bantları hesapla
        upper_band = ema_fish + range_offset
        lower_band = ema_fish - range_offset
        
        # Sonuç dataframe'i güncelle
        result_df['fisher'] = fisher
        result_df['trigger'] = trigger
        result_df['ema_fish'] = ema_fish
        result_df['upper_band'] = upper_band
        result_df['lower_band'] = lower_band
        
        logger.debug(f"Fisher Transform hesaplandı: {len(fisher)} veri noktası")
        return result_df
    
    except Exception as e:
        logger.error(f"Fisher Transform hesaplanırken hata: {e}")
        return df
