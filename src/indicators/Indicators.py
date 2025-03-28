# indicators/Indicators.py
from .rsi import rsi
from .macd import macd
from .vortex import vortex
from .atr import atr
from .t3 import t3MovingAverage


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
    def getT3(series, window=14, volume_factor=0.7):
        return t3MovingAverage(series, window, volume_factor)
