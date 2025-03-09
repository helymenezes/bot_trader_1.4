import pandas as pd
import numpy as np

def calculate_bollinger_bands(series, window=20, std=2):
    """
    Calcula as Bandas de Bollinger para uma série de preços.
    
    Parâmetros:
    -----------
    series : pd.Series ou pd.DataFrame
        Série de preços ou DataFrame contendo os preços
    window : int
        Período para cálculo da média móvel
    std : float
        Número de desvios padrão para as bandas superior e inferior
    """
    try:
        # Converter para Series se for DataFrame
        if isinstance(series, pd.DataFrame):
            if 'close_price' in series.columns:
                data = series['close_price']
            else:
                return None
        elif isinstance(series, pd.Series):
            data = series
        else:
            return None

        # Verificar se há dados suficientes
        if len(data) < window:
            return None

        # Remover valores nulos
        data = data.dropna()

        # Calcular a média móvel
        middle_band = data.rolling(window=window).mean()
        
        # Calcular o desvio padrão
        std_dev = data.rolling(window=window).std()
        
        # Calcular as bandas superior e inferior
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)

        # Criar DataFrame com os resultados
        result = pd.DataFrame({
            'middle': middle_band,
            'upper': upper_band,
            'lower': lower_band
        })

        # Verificar se os cálculos foram bem sucedidos
        if result.isnull().all().any():
            return None

        return result

    except Exception as e:
        print(f"Erro ao calcular Bandas de Bollinger: {str(e)}")
        return None