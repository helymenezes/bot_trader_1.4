# Calculo de indicador EMA
def ema(series, fast_window=7, slow_window= 25, long_window= 99):
    fast_ema = series.ewm(span=fast_window, adjust=False).mean()
    slow_ema = series.ewm(span=slow_window, adjust=False).mean()
    long_ema = series.ewm(span=long_window, adjust=False).mean()    
    return fast_ema, slow_ema, long_ema