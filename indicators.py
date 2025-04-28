import numpy as np
import pandas as pd
import logging

# Logging settings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('indicators')

def fisher_ema_band(df: pd.DataFrame, length: int = 21, ema_length: int = 50, range_offset: float = 2.0) -> pd.DataFrame:
    """
    Adapt Pine Script Fisher Transform indicator to Python
    
    Args:
        df: DataFrame containing OHLC data
        length: Fisher window length
        ema_length: Fisher's EMA length
        range_offset: Range factor for bands
    
    Returns:
        DataFrame containing indicator values
    """
    try:
        logger.debug(f"Calculating Fisher Transform: length={length}, ema_length={ema_length}, offset={range_offset}")
        
        # Copy records
        result_df = df.copy()
        
        # Calculate HL2 (High and Low average)
        hl2 = (df['high'] + df['low']) / 2
        
        # Find max and min values for each period
        max_h = hl2.rolling(window=length).max()
        min_l = hl2.rolling(window=length).min()
        
        # Create numpy arrays for nValue1 and nFish
        nValue1 = np.zeros(len(df))
        nFish = np.zeros(len(df))
        
        # We can't calculate for the first length rows (not enough data)
        for i in range(length, len(df)):
            # If range is 0, use default value 0.5
            if max_h[i] == min_l[i]:
                raw = 0.5
            else:
                # Calculate Value1: normalized hl2
                raw = (hl2[i] - min_l[i]) / (max_h[i] - min_l[i])
            
            # Apply Pine Script formula
            v1 = 0.33 * 2 * (raw - 0.5) + 0.67 * nValue1[i-1]
            
            # Check nValue2 limits (-0.99 to 0.99)
            if v1 > 0.99:
                v2 = 0.999
            elif v1 < -0.99:
                v2 = -0.999
            else:
                v2 = v1
            
            # Update nValue1
            nValue1[i] = v1
            
            # Apply Fisher transformation
            nFish[i] = 0.5 * np.log((1 + v2) / (1 - v2)) + 0.5 * nFish[i-1]
            
        # Convert to pandas series
        fisher = pd.Series(nFish, index=df.index)
        trigger = fisher.shift(1)  # Fisher 1 period shifted
        
        # Calculate EMA
        ema_fish = fisher.ewm(span=ema_length, adjust=False).mean()
        
        # Calculate upper and lower bands
        upper_band = ema_fish + range_offset
        lower_band = ema_fish - range_offset
        
        # Update result dataframe
        result_df['fisher'] = fisher
        result_df['trigger'] = trigger
        result_df['ema_fish'] = ema_fish
        result_df['upper_band'] = upper_band
        result_df['lower_band'] = lower_band
        
        logger.debug(f"Fisher Transform calculated: {len(fisher)} data points")
        return result_df
    
    except Exception as e:
        logger.error(f"Error calculating Fisher Transform: {e}")
        return df
