import pandas_ta as ta
import pandas as pd

def calculate_bollinger_bands(series, column='close_price', window=20, std_dev=2):
    """
    Calcula as Bandas de Bollinger para uma série de preços usando pandas_ta.
    
    Parâmetros:
    -----------
    data : pandas.DataFrame
        DataFrame contendo os dados de preço
    column : str, opcional (padrão='close_price')
        Nome da coluna contendo os preços para cálculo
    window : int, opcional (padrão=20)
        Período para o cálculo da média móvel
    std_dev : int, opcional (padrão=2)
        Número de desvios padrão para as bandas superior e inferior
    
    Retorna:
    --------
    pandas.DataFrame
        DataFrame original com as colunas adicionais:
        - bollinger_ma: Média móvel (BBM)
        - upper_band: Banda superior (BBU)
        - lower_band: Banda inferior (BBL)
        - bollinger_std: Desvio padrão (BBD)
    """
    # Criamos uma cópia para evitar modificar o DataFrame original
    result = series.copy()
    
    # Verifica se há dados suficientes
    if len(result) < window:
        raise ValueError(f"Dados insuficientes. São necessários pelo menos {window} períodos.")
    
    # Verifica se a coluna existe
    if column not in result.columns:
        raise ValueError(f"Coluna '{column}' não encontrada no DataFrame.")
    
    # Verifica se há valores nulos
    if result[column].isnull().any():
        result = result.dropna(subset=[column])
        
    # Cálculo das Bandas de Bollinger usando pandas_ta
    bb = ta.bbands(close=result[column], length=window, std=std_dev)
    
    if bb is None:
        raise ValueError("Falha ao calcular as Bandas de Bollinger. Verifique se os dados de entrada são válidos.")
    
    # As colunas do pandas_ta são diferentes das que estávamos esperando
    # O padrão é: BBL_20_2.0, BBM_20_2.0, BBU_20_2.0, BBB_20_2.0, BBP_20_2.0
    bb_cols = [col for col in bb.columns if col.startswith(('BBL_', 'BBM_', 'BBU_', 'BBB_'))]
    if len(bb_cols) < 3:
        raise ValueError("Resultado inesperado do cálculo das Bandas de Bollinger")
        
    # Mapeamento das colunas
    for col in bb_cols:
        if col.startswith('BBM_'):
            result['bollinger_ma'] = bb[col]
        elif col.startswith('BBU_'):
            result['upper_band'] = bb[col]
        elif col.startswith('BBL_'):
            result['lower_band'] = bb[col]
        elif col.startswith('BBB_'):
            result['bollinger_std'] = bb[col]
    
    return result