#Calculo do IFR(rsi)
import pandas_ta as ta

def calculate_ifr(series, column='close_price', window=14):
    """
    Calcula o Índice de Força Relativa (IFR/RSI) para uma série de preços usando pandas_ta.
    
    Parâmetros:
    -----------
    series : pandas.seriesFrame
        seriesFrame contendo os dados de preço
    column : str, opcional (padrão='close_price')
        Nome da coluna contendo os preços para cálculo
    window : int, opcional (padrão=14)
        Período para o cálculo do IFR
    
    Retorna:
    --------
    pandas.seriesFrame
        seriesFrame original com a coluna adicional 'rsi' contendo o Índice de Força Relativa
    """
    # Criamos uma cópia para evitar modificar o seriesFrame original
    result = series.copy()
    
    # Calcula o RSI usando pandas_ta
    result['rsi'] = ta.rsi(close=result[column], length=window)
    
    return result