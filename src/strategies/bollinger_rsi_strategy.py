import pandas as pd
# import numpy as np
# import sys
# import os

# Importar os indicadores
from indicators.bollinger import calculate_bollinger_bands
from indicators.ifr import calculate_ifr

def bollinger_rsi_strategy(stock_data: pd.DataFrame, 
                         bollinger_window=20, 
                         bollinger_std=2, 
                         rsi_window=14, 
                         rsi_oversold=30, 
                         rsi_overbought=70, 
                         verbose=True):
    """
    Estratégia de trading baseada em Bandas de Bollinger e IFR (Índice de Força Relativa).
    
    Parâmetros:
    -----------
    stock_data : pandas.DataFrame
        DataFrame contendo os dados de preço (deve conter uma coluna 'close_price')
    bollinger_window : int, opcional (padrão=20)
        Período para o cálculo da média móvel das Bandas de Bollinger
    bollinger_std : int, opcional (padrão=2)
        Número de desvios padrão para as bandas superior e inferior
    rsi_window : int, opcional (padrão=14)
        Período para o cálculo do IFR
    rsi_oversold : int, opcional (padrão=30)
        Limite inferior do IFR considerado para condição de sobrevendido
    rsi_overbought : int, opcional (padrão=70)
        Limite superior do IFR considerado para condição de sobrecomprado
    verbose : bool, opcional (padrão=True)
        Se True, imprime detalhes sobre os cálculos e a decisão de trading
    
    Retorna:
    --------
    bool ou None
        True para sinal de compra, False para sinal de venda, None caso não haja dados suficientes
    """
    # Criamos uma cópia para evitar o `SettingWithCopyWarning`
    stock_data = stock_data.copy()
    
    try:
        # Cálculo das Bandas de Bollinger
        stock_data = calculate_bollinger_bands(
            stock_data, 
            column='close_price', 
            window=bollinger_window, 
            std_dev=bollinger_std
        )
        
        # Cálculo do RSI (Índice de Força Relativa)
        stock_data = calculate_ifr(
            stock_data, 
            column='close_price', 
            window=rsi_window
        )
    except ValueError as e:
        if verbose:
            print(f"⚠️ Erro ao calcular indicadores: {str(e)}")
        return None
    
    # 🔹 REMOVE PERÍODOS INICIAIS COM NaN
    stock_data.dropna(subset=['bollinger_ma', 'upper_band', 'lower_band', 'rsi'], inplace=True)
    
    # Se não houver dados suficientes após remover os NaNs, retorna None
    if len(stock_data) < bollinger_window:
        if verbose:
            print("⚠️ Dados insuficientes após remoção de NaN. Pulando período...")
        return None
    
    # Obtém os valores mais recentes para análise
    last_close = stock_data['close_price'].iloc[-1]
    last_upper_band = stock_data['upper_band'].iloc[-1]
    last_lower_band = stock_data['lower_band'].iloc[-1]
    last_bollinger_ma = stock_data['bollinger_ma'].iloc[-1]
    last_rsi = stock_data['rsi'].iloc[-1]
    
    # Verificação de condições de compra e venda
    buy_condition = (last_close <= last_lower_band) and (last_rsi <= rsi_oversold)
    sell_condition = (last_close >= last_upper_band) and (last_rsi >= rsi_overbought)
    
    # Decisão de trading
    if sell_condition:
        trade_decision = False  # Vender
    elif buy_condition:
        trade_decision = True   # Comprar
    else:
        # No caso de não atender nenhuma condição, mantemos a tendência geral
        # Comparando o preço atual com a média móvel das Bandas de Bollinger
        trade_decision = last_close > last_bollinger_ma
    
    if verbose:
        print("-------")
        print("📊 Estratégia: Bandas de Bollinger + IFR")
        print(f" | Último Preço: {last_close:.3f}")
        print(f" | Banda Superior: {last_upper_band:.3f}")
        print(f" | Banda Média: {last_bollinger_ma:.3f}")
        print(f" | Banda Inferior: {last_lower_band:.3f}")
        print(f" | IFR: {last_rsi:.2f}")
        print(f" | Condição de Compra: {buy_condition}")
        print(f" | Condição de Venda: {sell_condition}")
        print(f' | Decisão: {"Comprar" if trade_decision == True else "Vender" if trade_decision == False else "Nenhuma"}')
        print("-------")
    
    return trade_decision


