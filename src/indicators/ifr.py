#Calculo do IFR(rsi)
import pandas_ta as ta
import pandas as pd
import numpy as np

def calculate_ifr(series, window=14, column=None):
    """
    Calcula o Índice de Força Relativa (IFR/RSI) para uma série de preços usando pandas_ta.
    
    Parâmetros:
    -----------
    series : pd.Series ou pd.DataFrame
        Série de preços ou DataFrame contendo os preços
    window : int
        Período para cálculo do RSI
    column : str, opcional
        Nome da coluna a ser usada se series for um DataFrame
    """
    try:
        # Handle DataFrame with column specification
        if isinstance(series, pd.DataFrame):
            if column is not None and column in series.columns:
                close = series[column]
            elif 'close_price' in series.columns:
                close = series['close_price']
            else:
                return None
        elif isinstance(series, pd.Series):
            close = series
        else:
            return None

        # Verificar se há dados suficientes
        if len(close) < window:
            return None

        # Remover valores nulos
        close = close.dropna()
        
        # Verificar novamente se há dados suficientes após remover nulos
        if len(close) < window:
            return None

        # Calcular o RSI
        rsi_values = ta.rsi(close=close, length=window)
        
        # Verificar se o cálculo foi bem sucedido
        if rsi_values is None or rsi_values.empty or rsi_values.isna().all():
            return None

        # Retornar DataFrame com coluna RSI
        return pd.DataFrame({'rsi': rsi_values})

    except Exception as e:
        print(f"Erro ao calcular RSI: {str(e)}")
        return None