import pandas_ta as ta
import pandas as pd

def estrategia_ichimoku(stock_data, tenkan_window=9, kijun_window=26, senkou_window=52):
    # Calculate Ichimoku components manually since pandas_ta.ichimoku() doesn't return all components
    high = stock_data['high_price']
    low = stock_data['low_price']
    close = stock_data['close_price']
    
    # Tenkan-sen (Conversion Line)
    tenkan_high = high.rolling(window=tenkan_window).max()
    tenkan_low = low.rolling(window=tenkan_window).min()
    conversion_line = (tenkan_high + tenkan_low) / 2
    
    # Kijun-sen (Base Line)
    kijun_high = high.rolling(window=kijun_window).max()
    kijun_low = low.rolling(window=kijun_window).min()
    base_line = (kijun_high + kijun_low) / 2
    
    # Senkou Span A (Leading Span A)
    span_a = ((conversion_line + base_line) / 2).shift(kijun_window)
    
    # Senkou Span B (Leading Span B)
    senkou_high = high.rolling(window=senkou_window).max()
    senkou_low = low.rolling(window=senkou_window).min()
    span_b = ((senkou_high + senkou_low) / 2).shift(kijun_window)
    
    # Chikou Span (Lagging Span)
    chikou_span = close.shift(-kijun_window)
    
    return conversion_line, base_line, span_a, span_b, chikou_span
