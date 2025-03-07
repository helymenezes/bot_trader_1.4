import pandas_ta as ta
import pandas as pd

def macd(series, fast_window=12, slow_window=26, signal_window=9):
    if not isinstance(series, pd.Series):
        series = pd.Series(series)
        
    # Ensure we have enough data points
    min_periods = max(fast_window, slow_window) + signal_window
    if len(series) < min_periods:
        return None, None, None
        
    macd_df = ta.macd(series, fast=fast_window, slow=slow_window, signal=signal_window)
    if macd_df is None or macd_df.empty:
        return None, None, None
        
    macd_line = macd_df[f'MACD_{fast_window}_{slow_window}_{signal_window}']
    signal_line = macd_df[f'MACDs_{fast_window}_{slow_window}_{signal_window}']
    histogram = macd_df[f'MACDh_{fast_window}_{slow_window}_{signal_window}']
    
    # Check if any of the components contain all NaN values
    if macd_line.isna().all() or signal_line.isna().all() or histogram.isna().all():
        return None, None, None
        
    return macd_line, signal_line, histogram

