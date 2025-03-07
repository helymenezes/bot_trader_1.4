import pandas as pd
from indicators import Indicators

def getEMAMACDTradeStrategy(stock_data: pd.DataFrame, 
                             verbose: bool = True, 
                             ema_fast_period: int = 7, 
                             ema_slow_period: int = 21, 
                             macd_fast_period: int = 12, 
                             macd_slow_period: int = 26, 
                             signal_window: int = 9,
                             long_window: int = 99):
    """
    Estratégia de trade baseada em EMA e MACD utilizando os módulos da pasta indicators.
    
    Parâmetros:
    - stock_data: pd.DataFrame contendo ao menos a coluna 'close_price'.
    - verbose: se True imprime informações detalhadas.
    - ema_fast_period: período para o cálculo da EMA rápida (default: 7).
    - ema_slow_period: período para o cálculo da EMA lenta (default: 25).
    - macd_fast_period: período rápido para cálculo do MACD (default: 12).
    - macd_slow_period: período lento para cálculo do MACD (default: 26).
    - signal_window: período da Signal Line do MACD (default: 9).
    - long_window: parâmetro extra utilizado na função getema (default: 99).
    
    Retorna:
    - True para sinal de compra e False para sinal de venda.
    """
    # Cria uma cópia dos dados para evitar SettingWithCopyWarning
    df = stock_data.copy()

    # Verifica se a coluna 'close_price' existe
    if 'close_price' not in df.columns:
        if verbose:
            print("⚠️ Coluna 'close_price' não encontrada em stock_data.")
        return None

    # Verifica se há dados suficientes
    min_periods = max(ema_fast_period, ema_slow_period, macd_slow_period, long_window)
    if len(df) < min_periods:
        if verbose:
            print("⚠️ Dados insuficientes para análise.")
        return None

    # Calcula as EMAs usando a função getema do módulo Indicators
    # Assume-se que a função retorne um DataFrame com colunas 'EMA_fast' e 'EMA_slow'
    fast_ema, slow_ema, long_ema = Indicators.getema(df['close_price'], fast_window=ema_fast_period, 
                               slow_window=ema_slow_period, long_window=long_window)
    
    # Calcula o MACD usando a função getMACD do módulo Indicators
    # Assume-se que a função retorne um DataFrame com colunas 'MACD' e 'Signal_Line'
    macd, signal_line, histogram = Indicators.getMACD(df['close_price'], fast_window=macd_fast_period, 
                                 slow_window=macd_slow_period, signal_window=signal_window)
    
    # Verifica se algum indicador retornou None
    if any(x is None for x in [fast_ema, slow_ema, long_ema, macd, signal_line, histogram]):
        if verbose:
            print("⚠️ Erro no cálculo dos indicadores.")
        return None

    # Adiciona os indicadores ao DataFrame
    df['EMA_fast'] = fast_ema
    df['EMA_slow'] = slow_ema
    df['EMA_long'] = long_ema
    df['MACD'] = macd
    df['Signal_Line'] = signal_line
    df['MACD_Histogram'] = histogram

    # Remove períodos com NaN resultantes dos cálculos
    df.dropna(inplace=True)
    if len(df) < 2:
        if verbose:
            print("⚠️ Dados insuficientes após o cálculo dos indicadores. Pulando período...")
        return None

    # Define o regime do mercado:
    # Bullish quando MACD está acima ou igual à Signal Line
    bullish_regime = df['MACD'].iloc[-1] >= df['Signal_Line'].iloc[-1]

    # Detecta cruzamentos a partir dos dois últimos registros
    bullish_crossover = (df['EMA_fast'].iloc[-2] < df['EMA_slow'].iloc[-2]) and (df['EMA_fast'].iloc[-1] > df['EMA_slow'].iloc[-1])
    bearish_crossover = (df['EMA_fast'].iloc[-2] > df['EMA_slow'].iloc[-2]) and (df['EMA_fast'].iloc[-1] < df['EMA_slow'].iloc[-1])

    # Define a decisão de trade com base no regime e nos cruzamentos
    if bullish_regime:
        if bullish_crossover:
            trade_decision = True  # Sinal de compra
            decision_str = "Comprar (Cruzamento de alta)"
        elif bearish_crossover:
            trade_decision = False  # Sinal de venda
            decision_str = "Vender (Cruzamento de baixa em regime bullish)"
        else:
            # Caso não haja cruzamento, utiliza a posição atual das EMAs
            trade_decision = df['EMA_fast'].iloc[-1] > df['EMA_slow'].iloc[-1]
            decision_str = "Comprar" if trade_decision else "Vender"
    else:
        # Em regime de desvalorização, a estratégia recomenda vender
        trade_decision = False
        decision_str = "Vender (Regime de desvalorização)"

    if verbose:
        print("-------")
        print("📊 Estratégia: EMA + MACD (usando módulo Indicators)")
        print(f" | Última EMA Rápida: {df['EMA_fast'].iloc[-1]:.3f}")
        print(f" | Última EMA Lenta: {df['EMA_slow'].iloc[-1]:.3f}")
        print(f" | Último MACD: {df['MACD'].iloc[-1]:.3f}")
        print(f" | Última Signal Line: {df['Signal_Line'].iloc[-1]:.3f}")
        print(f" | Regime: {'Valorização (Bullish)' if bullish_regime else 'Desvalorização (Bearish)'}")
        print(f" | Decisão: {decision_str}")
        print("-------")

    return trade_decision
