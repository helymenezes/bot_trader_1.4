# Description: Exponential Moving Average (EMA) indicator.
import pandas_ta as ta
import pandas as pd

def ema(series, fast_window=7, slow_window=25, long_window=99):
    if not isinstance(series, pd.Series):
        series = pd.Series(series)
    
    # Ensure we have enough data points for the calculations
    min_periods = max(fast_window, slow_window, long_window)
    if len(series) < min_periods:
        return None, None, None
        
    fast_ema = ta.ema(series, length=fast_window)
    slow_ema = ta.ema(series, length=slow_window)
    long_ema = ta.ema(series, length=long_window)
    
    # Check if any of the EMAs contain all NaN values
    if fast_ema.isna().all() or slow_ema.isna().all() or long_ema.isna().all():
        return None, None, None
        
    return fast_ema, slow_ema, long_ema
