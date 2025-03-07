# strategies/fgv_strategies.py
import pandas as pd
from indicators import Indicators

def getFVGTradeStrategy(stock_data: pd.DataFrame, fvg_threshold=0.005, verbose=True):
    # Call the static method directly instead of creating an instance
    df_with_fvg = Indicators.getfvg(stock_data, fvg_threshold)

    last_row = df_with_fvg.iloc[-1]
    trade_decision = None

    if last_row['bullish_fvg']:
        trade_decision = True  # Comprar
    elif last_row['bearish_fvg']:
        trade_decision = False  # Vender

    if verbose:
        print("-------")
        print("📊 Estratégia FVGTradeStrategy")
        print(f" | Último fechamento: {stock_data.iloc[-1]['close_price']:.4f}")
        print(f" | FVG Alta: {'Sim' if last_row['bullish_fvg'] else 'Não'}")
        print(f" | FVG Baixa: {'Sim' if last_row['bearish_fvg'] else 'Não'}")
        print(f" | Decisão: {'Comprar' if trade_decision else 'Vender' if trade_decision is False else 'Nenhuma'}")
        print("-------")

    return trade_decision
