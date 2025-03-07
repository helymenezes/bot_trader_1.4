import threading
import time
from modules.BinanceTraderBot import BinanceTraderBot
from binance.client import Client
from Models.StockStartModel import StockStartModel
import logging

# Define o logger
logging.basicConfig(
    filename="src/logs/trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

from strategies.moving_average_antecipation import getMovingAverageAntecipationTradeStrategy
from strategies.moving_average import getMovingAverageTradeStrategy


from strategies.rsi_strategy import getRsiTradeStrategy
from strategies.vortex_strategy import getVortexTradeStrategy
from strategies.ma_rsi_volume_strategy import getMovingAverageRSIVolumeStrategy
from strategies.ema_macd_strategy import getEMAMACDTradeStrategy
from strategies.ichimoku_strategy import ichimoku_trade_strategy
from strategies.bollinger_rsi_strategy import bollinger_rsi_strategy
from strategies.fvg_strategies import getFVGTradeStrategy

# fmt: off
# -------------------------------------------------------------------------------------------------
# 🟢🟢🟢 CONFIGURAÇÕES - PODEM ALTERAR - INICIO 🟢🟢🟢

# ------------------------------------------------------------------
# 🚀 AJUSTES DE ESTRATÉGIA 🚀

# 🏆 ESTRATÉGIA PRINCIPAL 🏆

# MAIN_STRATEGY = getMovingAverageAntecipationTradeStrategy
# MAIN_STRATEGY_ARGS = {"volatility_factor": 0.5, # Interfere na antecipação e nos lances de compra de venda limitados 
#                       "fast_window": 7,
#                       "slow_window": 21}

# MAIN_STRATEGY = getEMAMACDTradeStrategy
# MAIN_STRATEGY_ARGS = {
#     "verbose": False,
#     "ema_fast_period": 7,
#     "ema_slow_period": 25,
#     "macd_fast_period": 12,
#     "macd_slow_period": 26,
#     "signal_window": 9,
#     "long_window": 99
# }

# MAIN_STRATEGY = ichimoku_trade_strategy
# MAIN_STRATEGY_ARGS = {}

# MAIN_STRATEGY = getVortexTradeStrategy
# MAIN_STRATEGY_ARGS = {}

# MAIN_STRATEGY = getMovingAverageRSIVolumeStrategy
# MAIN_STRATEGY_ARGS = {  "fast_window":  9,
#                         "slow_window":  21,
#                         "rsi_window":  14,
#                         "rsi_overbought":  70,
#                         "rsi_oversold":  30,
#                         "volume_multiplier":  1.5
#                         }

# MAIN_STRATEGY = getRsiTradeStrategy
# MAIN_STRATEGY_ARGS = {}

# MAIN_STRATEGY = bollinger_rsi_strategy
# MAIN_STRATEGY_ARGS = {
#                         "bollinger_window":20, 
#                          "bollinger_std":2, 
#                          "rsi_window":14, 
#                          "rsi_oversold":30, 
#                          "rsi_overbought":70,
#                          }

MAIN_STRATEGY = getFVGTradeStrategy
MAIN_STRATEGY_ARGS = {}

# -----------------

# 🥈 ESTRATÉGIA DE FALLBACK (reserva) 🥈

FALLBACK_ACTIVATED = True     
FALLBACK_STRATEGY = getMovingAverageRSIVolumeStrategy
FALLBACK_STRATEGY_ARGS = {}

# ------------------------------------------------------------------
# 🛠️ AJUSTES TÉCNICOS 🛠️

# Ajustes de LOSS PROTECTION
ACCEPTABLE_LOSS_PERCENTAGE  = 0         # (Em base 100%) O quando o bot aceita perder de % (se for negativo, o bot só aceita lucro)
STOP_LOSS_PERCENTAGE        = 1.0       # (Em base 100%) % Máxima de loss que ele aceita para vender à mercado independente

# Ajustes de TAKE PROFIT (Em base 100%)                        
TP_AT_PERCENTAGE =      [2, 4, 8]       # Em [X%, Y%]                       
TP_AMOUNT_PERCENTAGE =  [50, 50, 100]   # Vende [A%, B%]


# ------------------------------------------------------------------
# ⌛ AJUSTES DE TEMPO

# CANDLE_PERIOD = Client.KLINE_INTERVAL_1HOUR # Périodo do candle análisado
CANDLE_PERIOD = Client.KLINE_INTERVAL_15MINUTE # Périodo do candle análisado

TEMPO_ENTRE_TRADES          = 15 * 60            # Tempo que o bot espera para verificar o mercado (em segundos)
DELAY_ENTRE_ORDENS          = 60 * 60           # Tempo que o bot espera depois de realizar uma ordem de compra ou venda (ajuda a diminuir trades de borda)


# ------------------------------------------------------------------
# 🪙 MOEDAS NEGOCIADAS

XRP_USDT = StockStartModel(  stockCode = "XRP",
                            operationCode = "XRPUSDT",
                            tradedQuantity = 0,
                            mainStrategy = MAIN_STRATEGY, mainStrategyArgs = MAIN_STRATEGY_ARGS, fallbackStrategy = FALLBACK_STRATEGY, fallbackStrategyArgs = FALLBACK_STRATEGY_ARGS,
                            candlePeriod = CANDLE_PERIOD, stopLossPercentage = STOP_LOSS_PERCENTAGE, tempoEntreTrades = TEMPO_ENTRE_TRADES, delayEntreOrdens = DELAY_ENTRE_ORDENS, acceptableLossPercentage = ACCEPTABLE_LOSS_PERCENTAGE, fallBackActivated= FALLBACK_ACTIVATED, takeProfitAtPercentage=TP_AT_PERCENTAGE, takeProfitAmountPercentage=TP_AMOUNT_PERCENTAGE)

SOL_USDT = StockStartModel(  stockCode = "SOL",
                            operationCode = "SOLUSDT",
                            tradedQuantity = 0.1,
                            mainStrategy = MAIN_STRATEGY, mainStrategyArgs = MAIN_STRATEGY_ARGS, fallbackStrategy = FALLBACK_STRATEGY, fallbackStrategyArgs = FALLBACK_STRATEGY_ARGS,
                            candlePeriod = CANDLE_PERIOD, stopLossPercentage = STOP_LOSS_PERCENTAGE, tempoEntreTrades = TEMPO_ENTRE_TRADES, delayEntreOrdens = DELAY_ENTRE_ORDENS, acceptableLossPercentage = ACCEPTABLE_LOSS_PERCENTAGE, fallBackActivated= FALLBACK_ACTIVATED, takeProfitAtPercentage=TP_AT_PERCENTAGE, takeProfitAmountPercentage=TP_AMOUNT_PERCENTAGE)

BTC_USDT = StockStartModel(  stockCode = "BTC",
                            operationCode = "BTCUSDT",
                            tradedQuantity = 0.01,
                            mainStrategy = MAIN_STRATEGY, mainStrategyArgs = MAIN_STRATEGY_ARGS, fallbackStrategy = FALLBACK_STRATEGY, fallbackStrategyArgs = FALLBACK_STRATEGY_ARGS,
                            candlePeriod = CANDLE_PERIOD, stopLossPercentage = STOP_LOSS_PERCENTAGE, tempoEntreTrades = TEMPO_ENTRE_TRADES, delayEntreOrdens = DELAY_ENTRE_ORDENS, acceptableLossPercentage = ACCEPTABLE_LOSS_PERCENTAGE, fallBackActivated= FALLBACK_ACTIVATED, takeProfitAtPercentage=TP_AT_PERCENTAGE, takeProfitAmountPercentage=TP_AMOUNT_PERCENTAGE)

BTC_USDC = StockStartModel(  stockCode = "BTC",
                            operationCode = "BTCBRL",
                            tradedQuantity = 0.001,
                            mainStrategy = MAIN_STRATEGY, mainStrategyArgs = MAIN_STRATEGY_ARGS, fallbackStrategy = FALLBACK_STRATEGY, fallbackStrategyArgs = FALLBACK_STRATEGY_ARGS,
                            candlePeriod = CANDLE_PERIOD, stopLossPercentage = STOP_LOSS_PERCENTAGE, tempoEntreTrades = TEMPO_ENTRE_TRADES, delayEntreOrdens = DELAY_ENTRE_ORDENS, acceptableLossPercentage = ACCEPTABLE_LOSS_PERCENTAGE, fallBackActivated= FALLBACK_ACTIVATED, takeProfitAtPercentage=TP_AT_PERCENTAGE, takeProfitAmountPercentage=TP_AMOUNT_PERCENTAGE)


# ⤵️ Array que DEVE CONTER as moedas que serão negociadas
stocks_traded_list = [XRP_USDT]

THREAD_LOCK = True # True = Executa 1 moeda por vez | False = Executa todas simultânemaente

# 🔴🔴🔴 CONFIGURAÇÕES - FIM 🔴🔴🔴
# -------------------------------------------------------------------------------------------------



# 🔁 LOOP PRINCIPAL

thread_lock = threading.Lock()

def trader_loop(stockStart: StockStartModel):
    MaTrader = BinanceTraderBot(stock_code = stockStart.stockCode
                                , operation_code = stockStart.operationCode
                                , traded_quantity = stockStart.tradedQuantity
                                , traded_percentage = stockStart.tradedPercentage
                                , candle_period = stockStart.candlePeriod
                                , time_to_trade = stockStart.tempoEntreTrades
                                , delay_after_order = stockStart.delayEntreOrdens
                                , acceptable_loss_percentage = stockStart.acceptableLossPercentage
                                , stop_loss_percentage = stockStart.stopLossPercentage
                                , fallback_activated = stockStart.fallBackActivated
                                , take_profit_at_percentage = stockStart.takeProfitAtPercentage
                                , take_profit_amount_percentage= stockStart.takeProfitAmountPercentage
                                , main_strategy = stockStart.mainStrategy
                                , main_strategy_args =  stockStart.mainStrategyArgs
                                , fallback_strategy = stockStart.fallbackStrategy
                                , fallback_strategy_args = stockStart.fallbackStrategyArgs)
    

    total_executed:int = 1

    while(True):
        if(THREAD_LOCK):
            with thread_lock:
                print(f"[{MaTrader.operation_code}][{total_executed}] '{MaTrader.operation_code}'")
                MaTrader.execute()
                print(f"^ [{MaTrader.operation_code}][{total_executed}] time_to_sleep = '{MaTrader.time_to_sleep/60:.2f} min'")
                print(f"------------------------------------------------")
                total_executed += 1
        else:
            print(f"[{MaTrader.operation_code}][{total_executed}] '{MaTrader.operation_code}'")
            MaTrader.execute()
            print(f"^ [{MaTrader.operation_code}][{total_executed}] time_to_sleep = '{MaTrader.time_to_sleep/60:.2f} min'")
            print(f"------------------------------------------------")
            total_executed += 1
        time.sleep(MaTrader.time_to_sleep)


# Criando e iniciando uma thread para cada objeto
threads = []

for asset in stocks_traded_list:
    thread = threading.Thread(target=trader_loop, args=(asset,))
    thread.daemon = True  # Permite finalizar as threads ao encerrar o programa
    thread.start()
    threads.append(thread)

print("Threads iniciadas para todos os ativos.")

# O programa principal continua executando sem bloquear
try:
    while True:
        time.sleep(1)  # Mantenha o programa rodando
except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuário.")

# -----------------------------------------------------------------

# fmt: on
