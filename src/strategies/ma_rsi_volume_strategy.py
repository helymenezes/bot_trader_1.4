import pandas as pd
import numpy as np
from indicators import Indicators

def getMovingAverageRSIVolumeStrategy(stock_data: pd.DataFrame,
                                     verbose: bool = True,
                                     fast_window: int = 9,
                                     slow_window: int = 21,
                                     rsi_window: int = 14,
                                     rsi_overbought: int = 70,
                                     rsi_oversold: int = 30,
                                     volume_multiplier: float = 1.5):
    """
    Estratégia de trade baseada em Médias Móveis com confirmação de RSI e Volume.
    """
    df = stock_data.copy()

    if 'close_price' not in df.columns:
        if verbose:
            print("⚠️ Coluna 'close_price' não encontrada em stock_data.")
        return None

    # Calcula as EMAs
    fast_ema, slow_ema, _ = Indicators.getema(df['close_price'], 
                                             fast_window=fast_window, 
                                             slow_window=slow_window)

    # Calcula o RSI
    rsi_data = Indicators.getifr(df['close_price'], window=rsi_window)

    # Verifica se os cálculos foram bem sucedidos
    if any(x is None for x in [fast_ema, slow_ema]) or rsi_data is None:
        if verbose:
            print("⚠️ Erro no cálculo dos indicadores.")
        return None

    # Adiciona os indicadores ao DataFrame
    df['ma_fast'] = fast_ema
    df['ma_slow'] = slow_ema
    df['rsi'] = rsi_data['rsi']

    # Calcula a média do volume
    df['volume_avg'] = df['volume'].rolling(window=min(slow_window, 14)).mean()

    # Remove períodos com NaN
    df.dropna(inplace=True)
    if len(df) < 2:
        if verbose:
            print("⚠️ Dados insuficientes após o cálculo dos indicadores.")
        return None

    # Últimos valores dos indicadores
    last_ma_fast = df['ma_fast'].iloc[-1]
    last_ma_slow = df['ma_slow'].iloc[-1]
    last_rsi = df['rsi'].iloc[-1]
    last_volume = df['volume'].iloc[-1]
    last_volume_avg = df['volume_avg'].iloc[-1]

    # Condições para compra
    buy_condition = (
        (last_ma_fast > last_ma_slow) and 
        (last_rsi > rsi_oversold) and 
        (last_rsi < rsi_overbought) and
        (last_volume > (volume_multiplier * last_volume_avg))
    )

    # Condições para venda
    sell_condition = (
        (last_ma_fast < last_ma_slow) or
        (last_rsi > rsi_overbought)
    )

    # Define a decisão de trade
    if buy_condition:
        trade_decision = True
        decision_str = "Comprar"
    elif sell_condition:
        trade_decision = False
        decision_str = "Vender"
    else:
        trade_decision = None
        decision_str = "Aguardar"

    if verbose:
        print("-------")
        print("📊 Estratégia: Médias Móveis + RSI + Volume")
        print(f" | MA Rápida: {last_ma_fast:.3f}")
        print(f" | MA Lenta: {last_ma_slow:.3f}")
        print(f" | RSI: {last_rsi:.3f}")
        print(f" | Volume: {last_volume:.3f}")
        print(f" | Volume Médio: {last_volume_avg:.3f}")
        print(f" | Decisão: {decision_str}")
        print("-------")

    return trade_decision
