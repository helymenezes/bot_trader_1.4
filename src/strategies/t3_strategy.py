import pandas as pd
from indicators.t3 import t3MovingAverage


# Estratégia baseada no cruzamento das T3 MA
def getT3MATradeStrategy(stock_data: pd.DataFrame, 
                         fast_period=7, 
                         slow_period=40, 
                         volume_factor=0.7, 
                         verbose=True):
    """
    Estratégia de trading com o indicador T3 Moving Average.

    Parâmetros:
    - stock_data: DataFrame com coluna obrigatória 'close' ou 'close_price'.
    - fast_period: Período curto da T3 MA rápida.
    - slow_period: Período longo da T3 MA lenta.
    - volume_factor: Fator de suavização T3 (padrão 0.7).
    - verbose: Se True, exibe informações detalhadas.

    Retorno:
    - True para Compra, False para Venda, None se insuficiente.
    """

    stock_data = stock_data.copy()

    # Verificar se a coluna 'close' ou 'close_price' está disponível
    if 'close' in stock_data.columns:
        close_col = 'close'
    elif 'close_price' in stock_data.columns:
        close_col = 'close_price'
    else:
        raise ValueError("⚠️ A coluna 'close' ou 'close_price' é obrigatória nos dados fornecidos.")
    
    # Normalizando os nomes das colunas para compatibilidade com o indicador T3
    data_for_t3 = stock_data.copy()
    if 'close_price' in stock_data.columns and 'close' not in stock_data.columns:
        data_for_t3['close'] = stock_data['close_price']
    if 'high_price' in stock_data.columns and 'high' not in stock_data.columns:
        data_for_t3['high'] = stock_data['high_price']
    if 'low_price' in stock_data.columns and 'low' not in stock_data.columns:
        data_for_t3['low'] = stock_data['low_price']

    # Calcular as médias móveis T3 rápida e lenta
    stock_data['t3_fast'] = t3MovingAverage(data_for_t3, period=fast_period, volume_factor=volume_factor)
    stock_data['t3_slow'] = t3MovingAverage(data_for_t3, period=slow_period, volume_factor=volume_factor)

    # Remover NaNs resultantes
    stock_data.dropna(subset=['t3_fast', 't3_slow'], inplace=True)

    # Verificar se há dados suficientes após remover NaNs
    if len(stock_data) < slow_period:
        if verbose:
            print("⚠️ Dados insuficientes após remoção de NaN. Pulando período...")
        return None

    # Últimas T3 MA calculadas
    last_t3_fast = stock_data['t3_fast'].iloc[-1]
    last_t3_slow = stock_data['t3_slow'].iloc[-1]

    # Decisão baseada no cruzamento das T3 MAs
    trade_decision = last_t3_fast > last_t3_slow  # True=Compra, False=Venda

    if verbose:
        print("-------")
        print("📊 Estratégia: T3 Moving Average (Tillson)")
        print(f" | Última T3 MA Rápida ({fast_period}): {last_t3_fast:.5f}")
        print(f" | Última T3 MA Lenta ({slow_period}): {last_t3_slow:.5f}")
        print(f" | Decisão: {'🟢 Comprar' if trade_decision else '🔴 Vender'}")
        print("-------")

    return trade_decision
