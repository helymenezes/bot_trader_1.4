from modules.BinanceTraderBot import BinanceTraderBot
from binance.client import Client
from tests.backtestRunner import backtestRunner
from strategies.ut_bot_alerts import *
from strategies.moving_average_antecipation import getMovingAverageAntecipationTradeStrategy
from strategies.moving_average import getMovingAverageTradeStrategy
from strategies.rsi_strategy import getRsiTradeStrategy
from strategies.vortex_strategy import getVortexTradeStrategy
from strategies.ma_rsi_volume_strategy import getMovingAverageRSIVolumeStrategy
from strategies.ema_macd_strategy import getEMAMACDTradeStrategy
from strategies.ichimoku_strategy import ichimoku_trade_strategy
from strategies.bollinger_rsi_strategy import bollinger_rsi_strategy
from strategies.fvg_strategies import getFVGTradeStrategy


# ------------------------------------------------------------------------
# 🔎 AJUSTES BACKTESTS 🔎

STOCK_CODE = "XRP"  # Código da Criptomoeda
OPERATION_CODE = "XRPUSDT"  # Código da operação (cripto + moeda)
INITIAL_BALANCE = 1000  # Valor de investimento inicial em USDT ou BRL

# ----------------------------------------
# 📊 PERÍODO DO CANDLE, SELECIONAR 1 📊

CANDLE_PERIOD = Client.KLINE_INTERVAL_1HOUR

# CANDLE_PERIOD = Client.KLINE_INTERVAL_15MINUTE

CLANDES_RODADOS = 7 * 24  #  dias de 24 horas

# ------------------------------------------------------------------------
# ⏬ SELEÇÃO DE ESTRATÉGIAS ⏬

devTrader = BinanceTraderBot(
    stock_code=STOCK_CODE,
    operation_code=OPERATION_CODE,
    traded_quantity=0,
    traded_percentage=100,
    candle_period=CANDLE_PERIOD,
    # volatility_factor=VOLATILITY_FACTOR,
)


devTrader.updateAllData()

print(f"\n{STOCK_CODE} - UT BOTS - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=utBotAlerts,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    atr_multiplier=2,
    atr_period=1,
    verbose=False,
)

devTrader.updateAllData()

print(f"\n{STOCK_CODE} - MA RSI e VOLUME - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=getMovingAverageRSIVolumeStrategy,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    verbose=False,
)


print(f"\n{STOCK_CODE} - MA ANTECIPATION - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=getMovingAverageAntecipationTradeStrategy,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    volatility_factor=0.5,
    fast_window=7,
    slow_window=40,
    verbose=False,
)

print(f"\n{STOCK_CODE} - MA SIMPLES FALLBACK - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=getMovingAverageTradeStrategy,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    fast_window=7,
    slow_window=40,
    verbose=False,
)

print(f"\n{STOCK_CODE} - RSI - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=getRsiTradeStrategy,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    low=30,
    high=70,
    verbose=False,
)

print(f"\n{STOCK_CODE} - VORTEX - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=getVortexTradeStrategy,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    verbose=False,
)

print(f"\n{STOCK_CODE} - EMA + MACD - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=getEMAMACDTradeStrategy,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    ema_fast_period=7,  # Changed from 9 to 7 to match default
    ema_slow_period=21,  # Changed from 1 to 21 - more reasonable value
    macd_fast_period=12,
    macd_slow_period=26,
    signal_window=9,
    verbose=False,
)


print(f"\n{STOCK_CODE} - Ichimoku - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=ichimoku_trade_strategy,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    verbose=False,
)

print(f"\n{STOCK_CODE} - Bollinger RSI - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=bollinger_rsi_strategy,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    verbose=False,
)

print(f"\n{STOCK_CODE} - FVG - {str(CANDLE_PERIOD)}")
backtestRunner(
    stock_data=devTrader.stock_data,
    strategy_function=getFVGTradeStrategy,
    periods=CLANDES_RODADOS,
    initial_balance=INITIAL_BALANCE,
    verbose=False,
)



print("\n\n")
