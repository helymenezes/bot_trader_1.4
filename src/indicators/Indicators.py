# indicators/Indicators.py
from .rsi import rsi
from .vortex import vortex
from .atr import atr
from .ema import ema
from .macd import macd
from .ichimoku import estrategia_ichimoku
from .bollinger import calculate_bollinger_bands
from .ifr import calculate_ifr
from .fvg import calculate_fvg


class Indicators:
    @staticmethod
    def getRSI(series, window=14, last_only=True):
        return rsi(series, window, last_only)


    @staticmethod
    def getMACD(series, fast_window=12, slow_window=26, signal_window=9):
        return macd(series, fast_window, slow_window, signal_window)

    @staticmethod
    def getVortex(series, window=14, positive=True):
        return vortex(series, window, positive)

    @staticmethod
    def getAtr(series, window=14):
        return atr(series, window)
    
    @staticmethod
    def getema(series, fast_window=7, slow_window= 25, long_window= 99):
        return ema(series, fast_window, slow_window, long_window)
    
    @staticmethod
    def getIchimoku(stock_data, tenkan_window=9, kijun_window=26, senkou_window=52):
        return estrategia_ichimoku(stock_data, tenkan_window, kijun_window, senkou_window)
    
    @staticmethod
    def getBollinger(series, window=20, std=2):
        return calculate_bollinger_bands(series, window, std)
    
    @staticmethod
    def getifr(series, window=14):
        return calculate_ifr(series, window)
    
    @staticmethod
    def getfvg(stock_data, threshold=0.005):
        """Calcula FVG básico"""
        return calculate_fvg(stock_data, threshold)

    

   
