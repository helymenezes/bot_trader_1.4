import pandas as pd
from indicators.ichimoku import estrategia_ichimoku

def ichimoku_trade_strategy(stock_data: pd.DataFrame, tenkan_window=9, kijun_window=26, senkou_window=52, verbose=True):
    stock_data = stock_data.copy()

    tenkan, kijun, senkou_a, senkou_b, chikou = estrategia_ichimoku(
        stock_data, tenkan_window, kijun_window, senkou_window
    )

    stock_data['Tenkan'] = tenkan
    stock_data['Kijun'] = kijun
    stock_data['SenkouA'] = senkou_a
    stock_data['SenkouB'] = senkou_b
    stock_data['Chikou'] = chikou

    # Remover NaNs resultantes dos cálculos
    stock_data.dropna(inplace=True)

    if stock_data.empty:
        if verbose:
            print("⚠️ Dados insuficientes após cálculo Ichimoku. Pulando período...")
        return None

    # Condição de compra
    condicao_compra = (stock_data['close_price'] > stock_data['SenkouA']) & \
                      (stock_data['close_price'] > stock_data['SenkouB']) & \
                      (stock_data['Tenkan'] > stock_data['Kijun'])

    # Condição de venda
    condicao_venda = (stock_data['close_price'] < stock_data['SenkouA']) & \
                     (stock_data['close_price'] < stock_data['SenkouB']) & \
                     (stock_data['Tenkan'] < stock_data['Kijun'])

    ultimo_sinal = None
    if condicao_compra.iloc[-1]:
        trade_decision = True  # Comprar
    elif condicao_venda.iloc[-1]:
        trade_decision = False  # Vender
    else:
        trade_decision = False  # Default em caso de sinal neutro ou indefinido

    if verbose:
        print("-------")
        print("📊 Estratégia: Ichimoku Cloud")
        print(f" | Último preço: {stock_data['close_price'].iloc[-1]:.3f}")
        print(f" | Tenkan-sen: {tenkan.iloc[-1]:.3f}")
        print(f" | Kijun-sen: {kijun.iloc[-1]:.3f}")
        print(f" | Senkou Span A: {senkou_a.iloc[-1]:.3f}")
        print(f" | Senkou Span B: {senkou_b.iloc[-1]:.3f}")
        print(f" | Decisão: {'Comprar 📈' if trade_decision else 'Vender 📉'}")
        print("-------")

    return trade_decision
