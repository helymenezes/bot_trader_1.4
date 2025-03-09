import pandas as pd
from indicators import Indicators

def bollinger_rsi_strategy(stock_data: pd.DataFrame,
                         verbose: bool = True,
                         window: int = 20,
                         std_dev: float = 2.0,
                         rsi_window: int = 14,
                         rsi_overbought: int = 70,
                         rsi_oversold: int = 30):
    """
    Estratégia de trading que combina Bandas de Bollinger com RSI
    """
    try:
        # Cria uma cópia dos dados para evitar avisos do pandas
        df = stock_data.copy()

        # Verifica se a coluna 'close_price' existe
        if 'close_price' not in df.columns:
            if verbose:
                print("⚠️ Coluna 'close_price' não encontrada em stock_data.")
            return None

        # Prepara os dados de preço
        close_series = pd.Series(df['close_price'].values, index=df.index)

        # Calcula as Bandas de Bollinger
        bollinger = Indicators.getBollinger(close_series, window=window, std=std_dev)
        if bollinger is None or not isinstance(bollinger, pd.DataFrame):
            if verbose:
                print("⚠️ Erro ao calcular Bandas de Bollinger.")
            return None

        # Calcula o RSI
        rsi_data = Indicators.getifr(close_series, window=rsi_window)
        if rsi_data is None or not isinstance(rsi_data, pd.DataFrame) or 'rsi' not in rsi_data.columns:
            if verbose:
                print("⚠️ Erro ao calcular RSI.")
            return None

        # Adiciona os indicadores ao DataFrame
        df['upper_band'] = bollinger['upper']
        df['middle_band'] = bollinger['middle']
        df['lower_band'] = bollinger['lower']
        df['rsi'] = rsi_data['rsi']

        # Remove dados ausentes
        df.dropna(inplace=True)
        if len(df) < 2:
            if verbose:
                print("⚠️ Dados insuficientes após cálculo dos indicadores.")
            return None

        # Obtém o último preço e valores dos indicadores
        last_close = df['close_price'].iloc[-1]
        last_upper = df['upper_band'].iloc[-1]
        last_lower = df['lower_band'].iloc[-1]
        last_rsi = df['rsi'].iloc[-1]

        # Define as condições de compra e venda
        buy_condition = (
            last_close <= last_lower and  # Preço próximo ou abaixo da banda inferior
            last_rsi <= rsi_oversold      # RSI indica sobrevenda
        )

        sell_condition = (
            last_close >= last_upper and  # Preço próximo ou acima da banda superior
            last_rsi >= rsi_overbought    # RSI indica sobrecompra
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
            print("📊 Estratégia: Bollinger + RSI")
            print(f" | Último preço: {last_close:.3f}")
            print(f" | Banda Superior: {last_upper:.3f}")
            print(f" | Banda Inferior: {last_lower:.3f}")
            print(f" | RSI: {last_rsi:.3f}")
            print(f" | Decisão: {decision_str}")
            print("-------")

        return trade_decision

    except Exception as e:
        if verbose:
            print(f"⚠️ Erro ao executar estratégia: {str(e)}")
        return None


