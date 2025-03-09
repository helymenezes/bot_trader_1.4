import pandas as pd
import numpy as np
from indicators import Indicators

def getMovingAverageRSIVolumeStrategy(
    stock_data: pd.DataFrame,
    fast_window: int = 9,
    slow_window: int = 21,
    rsi_window: int = 14,
    rsi_overbought: int = 70,
    rsi_oversold: int = 30,
    volume_multiplier: float = 1.5,
    price_action_confirmation: bool = True,
    trend_confirmation_periods: int = 3,
    exit_rsi_buffer: int = 5,
    trailing_stop_atr_factor: float = 2.0,
    atr_period: int = 14,
    verbose: bool = True,
):
    """
    Estratégia de Médias Móveis com confirmação de RSI, Volume e Price Action.
    """
    try:
        stock_data = stock_data.copy()

        # Prepara dados para ATR
        df_for_atr = pd.DataFrame({
            'high': stock_data['high_price'],
            'low': stock_data['low_price'],
            'close': stock_data['close_price']
        })

        # Calcula indicadores
        fast_ema, slow_ema, _ = Indicators.getema(stock_data["close_price"], 
                                               fast_window=fast_window, 
                                               slow_window=slow_window)
        
        rsi_data = Indicators.getifr(stock_data["close_price"], window=rsi_window)
        atr_values = Indicators.getAtr(df_for_atr, window=atr_period)

        # Verifica retorno dos indicadores
        if any(x is None for x in [fast_ema, slow_ema]) or rsi_data is None or atr_values is None:
            if verbose:
                print("⚠️ Erro no cálculo dos indicadores.")
            return None

        # Adiciona indicadores ao DataFrame
        stock_data["ma_fast"] = fast_ema
        stock_data["ma_slow"] = slow_ema
        stock_data["rsi"] = rsi_data['rsi'] if isinstance(rsi_data, pd.DataFrame) else None
        stock_data["atr"] = atr_values

        # Verifica valores nulos
        if (stock_data["ma_fast"].isnull().all() or 
            stock_data["ma_slow"].isnull().all() or 
            stock_data["rsi"].isnull().all() or 
            stock_data["atr"].isnull().all()):
            if verbose:
                print("⚠️ Indicadores retornaram valores nulos.")
            return None

        # Calcula média do volume
        stock_data["volume_avg"] = stock_data["volume"].rolling(window=min(slow_window, 14)).mean()

        # Price action features
        stock_data["body_size"] = abs(stock_data["close_price"] - stock_data["open_price"])
        stock_data["upper_shadow"] = stock_data["high_price"] - stock_data[["open_price", "close_price"]].max(axis=1)
        stock_data["lower_shadow"] = stock_data[["open_price", "close_price"]].min(axis=1) - stock_data["low_price"]
        stock_data["is_bullish"] = stock_data["close_price"] > stock_data["open_price"]

        # Remove NaN
        stock_data.dropna(subset=["ma_fast", "ma_slow", "rsi", "volume_avg", "atr"], inplace=True)

        if len(stock_data) < slow_window:
            if verbose:
                print("⚠️ Dados insuficientes após remoção de NaN.")
            return None

        # Análise de tendência
        trend_up_count = 0
        trend_down_count = 0
        
        for i in range(1, min(trend_confirmation_periods + 1, len(stock_data))):
            if stock_data["ma_fast"].iloc[-i] > stock_data["ma_slow"].iloc[-i]:
                trend_up_count += 1
            elif stock_data["ma_fast"].iloc[-i] < stock_data["ma_slow"].iloc[-i]:
                trend_down_count += 1
        
        strong_uptrend = trend_up_count >= trend_confirmation_periods
        strong_downtrend = trend_down_count >= trend_confirmation_periods

        # Últimos valores dos indicadores
        last_ma_fast = stock_data["ma_fast"].iloc[-1]
        last_ma_slow = stock_data["ma_slow"].iloc[-1]
        last_rsi = stock_data["rsi"].iloc[-1]
        last_volume = stock_data["volume"].iloc[-1]
        last_volume_avg = stock_data["volume_avg"].iloc[-1]
        last_atr = stock_data["atr"].iloc[-1]
        last_is_bullish = stock_data["is_bullish"].iloc[-1]

        # Price action signals
        if price_action_confirmation:
            price_action_buy_signal = (
                last_is_bullish and 
                stock_data["body_size"].iloc[-1] > stock_data["body_size"].rolling(5).mean().iloc[-1] and
                stock_data["lower_shadow"].iloc[-1] < stock_data["body_size"].iloc[-1] * 0.3
            )
            
            price_action_sell_signal = (
                not last_is_bullish and 
                stock_data["body_size"].iloc[-1] > stock_data["body_size"].rolling(5).mean().iloc[-1] and
                stock_data["upper_shadow"].iloc[-1] < stock_data["body_size"].iloc[-1] * 0.3
            )
        else:
            price_action_buy_signal = True
            price_action_sell_signal = True

        # Condições de compra
        buy_condition = (
            strong_uptrend and
            (last_ma_fast > last_ma_slow) and 
            (last_rsi > rsi_oversold) and 
            (last_rsi < rsi_overbought - 10) and
            (last_volume > (volume_multiplier * last_volume_avg)) and
            price_action_buy_signal
        )

        # Condições de venda
        sell_condition = (
            (last_ma_fast < last_ma_slow and strong_downtrend) or
            (last_rsi > rsi_overbought - exit_rsi_buffer) or
            (not price_action_sell_signal if price_action_confirmation else False)
        )

        # Trailing stop
        if "previous_buy_price" in stock_data.columns and not pd.isna(stock_data["previous_buy_price"].iloc[-1]):
            buy_price = stock_data["previous_buy_price"].iloc[-1]
            current_price = stock_data["close_price"].iloc[-1]
            
            if current_price > buy_price * 1.02:
                trailing_stop_level = current_price - (last_atr * trailing_stop_atr_factor)
                if stock_data["low_price"].iloc[-1] < trailing_stop_level:
                    sell_condition = True
                    if verbose:
                        print(f" | ⚠️ Trailing Stop ativado em: {trailing_stop_level:.3f}")

        trade_decision = True if buy_condition else False if sell_condition else None

        if verbose:
            print("-------")
            print("📊 Estratégia: MA + RSI + ATR")
            print(f" | MA Rápida: {last_ma_fast:.3f}")
            print(f" | MA Lenta: {last_ma_slow:.3f}")
            print(f" | RSI: {last_rsi:.3f}")
            print(f" | Volume: {last_volume:.3f}")
            print(f" | Volume Médio: {last_volume_avg:.3f}")
            print(f" | ATR: {last_atr:.3f}")
            print(f" | Tendência Alta: {strong_uptrend}")
            print(f" | Tendência Baixa: {strong_downtrend}")
            if price_action_confirmation:
                print(f" | PA Buy Signal: {price_action_buy_signal}")
                print(f" | PA Sell Signal: {price_action_sell_signal}")
            print(f' | Decisão: {"Comprar" if trade_decision else "Vender" if trade_decision is False else "Aguardar"}')
            print("-------")

        return trade_decision

    except Exception as e:
        if verbose:
            print(f"⚠️ Erro ao executar estratégia: {str(e)}")
        return None