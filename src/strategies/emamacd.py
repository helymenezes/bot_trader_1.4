import pandas as pd
import numpy as np
from indicators import Indicators

def getemaMacd(
    stock_data: pd.DataFrame,
    fast_ema=12,
    slow_ema=26,
    signal_period=9,
    price_column="close_price",
    verbose=True
):
    """
    Estratégia de trading baseada no cruzamento de EMA (Média Móvel Exponencial) 
    e indicador MACD para identificar momentos de compra e venda.
    
    Parameters:
    -----------
    stock_data : pd.DataFrame
        DataFrame contendo os dados do ativo com pelo menos a coluna 'close_price'
    fast_ema : int, opcional
        Período da EMA rápida (padrão: 12)
    slow_ema : int, opcional
        Período da EMA lenta (padrão: 26)
    signal_period : int, opcional
        Período para cálculo da linha de sinal do MACD (padrão: 9)
    price_column : str, opcional
        Nome da coluna de preços (padrão: 'close_price')
    verbose : bool, opcional
        Se True, exibe informações detalhadas (padrão: True)
        
    Returns:
    --------
    bool ou None:
        True para compra, False para venda, None se não houver decisão
    """
    # Criamos uma cópia para evitar o `SettingWithCopyWarning`
    stock_data = stock_data.copy()
    
    # Utilizando os indicadores já implementados
    # Obtém o MACD usando o módulo Indicators existente
    macd_line, macd_signal, macd_histogram = Indicators.getMACD(
        stock_data[price_column], 
        fast_window=fast_ema, 
        slow_window=slow_ema, 
        signal_window=signal_period
    )
    
    # Adiciona os resultados ao DataFrame
    stock_data["macd_line"] = macd_line
    stock_data["macd_signal"] = macd_signal
    stock_data["macd_histogram"] = macd_histogram
    
    # Como não há getEMA direto, calculamos manualmente as EMAs
    stock_data["ema_fast"] = stock_data[price_column].ewm(span=fast_ema, adjust=False).mean()
    stock_data["ema_slow"] = stock_data[price_column].ewm(span=slow_ema, adjust=False).mean()
    
    # Identifica cruzamentos
    stock_data["ema_cross_up"] = (
        (stock_data["ema_fast"].shift(1) <= stock_data["ema_slow"].shift(1)) &
        (stock_data["ema_fast"] > stock_data["ema_slow"])
    )
    stock_data["ema_cross_down"] = (
        (stock_data["ema_fast"].shift(1) >= stock_data["ema_slow"].shift(1)) &
        (stock_data["ema_fast"] < stock_data["ema_slow"])
    )
    stock_data["macd_cross_up"] = (
        (stock_data["macd_line"].shift(1) <= stock_data["macd_signal"].shift(1)) &
        (stock_data["macd_line"] > stock_data["macd_signal"])
    )
    stock_data["macd_cross_down"] = (
        (stock_data["macd_line"].shift(1) >= stock_data["macd_signal"].shift(1)) &
        (stock_data["macd_line"] < stock_data["macd_signal"])
    )
    
    # Verifica tendência da EMA (inclinação)
    stock_data["ema_slow_slope"] = stock_data["ema_slow"] - stock_data["ema_slow"].shift(3)
    
    # Remove NaNs gerados pelos cálculos
    stock_data.dropna(subset=["ema_fast", "ema_slow", "macd_line", "macd_signal"], inplace=True)
    
    # Se não houver dados suficientes, retorna None
    if len(stock_data) < slow_ema + signal_period:
        if verbose:
            print("⚠️ Dados insuficientes após remoção de NaN. Pulando período...")
        return None
    
    # Obtém os últimos valores para análise
    last_ema_fast = stock_data["ema_fast"].iloc[-1]
    last_ema_slow = stock_data["ema_slow"].iloc[-1]
    last_macd = stock_data["macd_line"].iloc[-1]
    last_signal = stock_data["macd_signal"].iloc[-1]
    last_histogram = stock_data["macd_histogram"].iloc[-1]
    last_ema_slope = stock_data["ema_slow_slope"].iloc[-1]
    
    # Identifica cruzamentos recentes (últimos 3 períodos)
    recent_ema_cross_up = stock_data["ema_cross_up"].iloc[-3:].any()
    recent_ema_cross_down = stock_data["ema_cross_down"].iloc[-3:].any()
    recent_macd_cross_up = stock_data["macd_cross_up"].iloc[-3:].any()
    recent_macd_cross_down = stock_data["macd_cross_down"].iloc[-3:].any()
    
    # Lógica de decisão de trading
    # Condição de compra: EMA rápida acima da lenta OU cruzamento recente para cima
    # E MACD acima da linha de sinal OU cruzamento recente do MACD para cima
    # E inclinação positiva da EMA lenta (tendência de alta)
    buy_condition = (
        ((last_ema_fast > last_ema_slow) or recent_ema_cross_up) and
        ((last_macd > last_signal) or recent_macd_cross_up) and
        (last_ema_slope > 0)
    )
    
    # Condição de venda: EMA rápida abaixo da lenta OU cruzamento recente para baixo
    # OU MACD abaixo da linha de sinal OU cruzamento recente do MACD para baixo
    # OU inclinação negativa da EMA lenta (tendência de baixa)
    sell_condition = (
        ((last_ema_fast < last_ema_slow) or recent_ema_cross_down) or
        ((last_macd < last_signal) or recent_macd_cross_down) or
        (last_ema_slope < 0)
    )
    
    # Determina a decisão final
    if buy_condition and not sell_condition:
        trade_decision = True  # Comprar
    elif sell_condition:
        trade_decision = False  # Vender
    else:
        trade_decision = None  # Sem decisão clara
    
    if verbose:
        print("-------")
        print("📊 Estratégia: ema_macd_2")
        print(f" | EMA Rápida (EMA{fast_ema}): {last_ema_fast:.3f}")
        print(f" | EMA Lenta (EMA{slow_ema}): {last_ema_slow:.3f}")
        print(f" | Tendência EMA Lenta: {'Subindo' if last_ema_slope > 0 else 'Descendo'}")
        print(f" | MACD: {last_macd:.3f}")
        print(f" | Sinal MACD: {last_signal:.3f}")
        print(f" | Histograma MACD: {last_histogram:.3f}")
        
        if recent_ema_cross_up:
            print(" | ✅ Cruzamento recente da EMA para cima")
        if recent_ema_cross_down:
            print(" | ❌ Cruzamento recente da EMA para baixo")
        if recent_macd_cross_up:
            print(" | ✅ Cruzamento recente do MACD para cima")
        if recent_macd_cross_down:
            print(" | ❌ Cruzamento recente do MACD para baixo")
            
        print(f" | Decisão: {'Comprar' if trade_decision == True else 'Vender' if trade_decision == False else 'Nenhuma'}")
        print("-------")
    
    return trade_decision