import pandas as pd
from indicators import Indicators

def getVortexEmaRsiTradeStrategy(
    stock_data: pd.DataFrame,
    fast_window: int = 7,
    slow_window: int = 25,
    rsi_period: int = 14,
    volume_window: int = 20,
    verbose: bool = True
):
    """
    Estratégia de trade para criptomoedas que combina:
      - Médias Móveis Exponenciais (EMA) para identificação de tendência,
      - IFR/RSI para confirmação do momentum,
      - Confirmação de volume (volume atual > média móvel do volume).

    Parâmetros:
      - stock_data: pd.DataFrame com ao menos as colunas "close_price" e "volume".
      - fast_window: período para a EMA rápida (default 14).
      - slow_window: período para a EMA lenta (default 30).
      - rsi_period: período para o IFR/RSI (default 14).
      - volume_window: período para a média móvel do volume (default 20).
      - verbose: se True, imprime os detalhes dos indicadores e a decisão.

    Retorna:
      - True para sinal de compra,
      - False para sinal de venda,
      - None se não houver sinal claro.
    """
    try:
        # Cria uma cópia para evitar modificações no DataFrame original
        df = stock_data.copy()

        # Calcula as EMAs utilizando os cálculos disponíveis em indicators/ema.py
        fast_ema, slow_ema, _ = Indicators.getema(
            df["close_price"], 
            fast_window=fast_window, 
            slow_window=slow_window
        )
        
        if fast_ema is None or slow_ema is None:
            if verbose:
                print("⚠️ Erro ao calcular EMAs")
            return None

        # Calcula o IFR/RSI
        rsi_data = Indicators.getifr(df["close_price"], window=rsi_period)
        if rsi_data is None or not isinstance(rsi_data, pd.DataFrame):
            if verbose:
                print("⚠️ Erro ao calcular RSI")
            return None

        # Adiciona indicadores ao DataFrame
        df["ema_fast"] = fast_ema
        df["ema_slow"] = slow_ema
        df["rsi"] = rsi_data["rsi"]

        # Calcula a média móvel do volume para confirmação de liquidez
        df["vol_avg"] = df["volume"].rolling(window=volume_window).mean()

        # Remove os períodos iniciais com valores NaN
        df.dropna(subset=["ema_fast", "ema_slow", "rsi", "vol_avg"], inplace=True)

        # Se os dados forem insuficientes após a remoção de NaN, retorna None
        if len(df) < slow_window:
            if verbose:
                print("⚠️ Dados insuficientes após remoção de NaN. Pulando período...")
            return None

        # Obtém os últimos valores dos indicadores
        last_ema_fast = df["ema_fast"].iloc[-1]
        last_ema_slow = df["ema_slow"].iloc[-1]
        last_rsi = df["rsi"].iloc[-1]
        last_volume = df["volume"].iloc[-1]
        last_vol_avg = df["vol_avg"].iloc[-1]

        # Lógica de decisão:
        # - Compra se: EMA rápida > EMA lenta, RSI > 50 e volume atual > média do volume.
        # - Venda se: EMA rápida < EMA lenta, RSI < 50 e volume atual > média do volume.
        if last_ema_fast > last_ema_slow and last_rsi > 50 and last_volume > last_vol_avg:
            trade_decision = True
        elif last_ema_fast < last_ema_slow and last_rsi < 50 and last_volume > last_vol_avg:
            trade_decision = False
        else:
            trade_decision = None

        # Exibe informações detalhadas se verbose estiver ativo
        if verbose:
            print("-------")
            print("📊 Estratégia: Vortex + EMA + RSI")
            print(f" | Última EMA Rápida: {last_ema_fast:.3f}")
            print(f" | Última EMA Lenta: {last_ema_slow:.3f}")
            print(f" | Último RSI: {last_rsi:.3f}")
            print(f" | Último Volume: {last_volume}")
            print(f" | Média de Volume: {last_vol_avg:.2f}")
            print(f' | Decisão: {"Comprar" if trade_decision is True else "Vender" if trade_decision is False else "Nenhuma"}')
            print("-------")

        return trade_decision

    except Exception as e:
        if verbose:
            print(f"⚠️ Erro ao executar estratégia: {str(e)}")
        return None
