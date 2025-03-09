import pandas as pd
import numpy as np

"""
O que é ATR (Average True Range)?

O ATR (Average True Range) é um indicador técnico desenvolvido por J. Welles Wilder Jr. para medir a volatilidade
de um ativo financeiro. Ele calcula a média das variações reais do preço durante um determinado período.

O True Range (TR) é definido como o maior dos seguintes valores:

Alta atual - Baixa atual
Módulo da Alta atual - Fechamento anterior
Módulo da Baixa atual - Fechamento anterior
O ATR é obtido ao calcular a média móvel do True Range ao longo de um período específico, geralmente 14 períodos.
"""


def atr(data: pd.DataFrame, window=14):
    """
    Calcula o Average True Range (ATR) de um DataFrame contendo preços OHLC.
    """
    try:
        # Verificar se as colunas necessárias existem
        required_columns = ['high', 'low', 'close']
        if not all(col in data.columns for col in required_columns):
            return None

        # Copiar dados para evitar modificar o original
        df = data[required_columns].copy()
        
        # Remover valores nulos
        df.dropna(inplace=True)
        
        # Verificar se há dados suficientes
        if len(df) < window:
            return None

        # Cálculo do True Range (TR)
        tr1 = df["high"] - df["low"]
        tr2 = np.abs(df["high"] - df["close"].shift(1))
        tr3 = np.abs(df["low"] - df["close"].shift(1))

        # True Range é o maior valor entre os três cálculos
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # ATR é a média móvel do True Range
        atr_values = true_range.rolling(window=window).mean()

        # Verificar se o cálculo foi bem sucedido
        if atr_values is None or atr_values.empty or atr_values.isna().all():
            return None

        return atr_values

    except Exception as e:
        print(f"Erro ao calcular ATR: {str(e)}")
        return None
