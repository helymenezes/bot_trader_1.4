# indicators/fvg.py
import pandas as pd

def calculate_fvg(stock_data: pd.DataFrame, threshold=0.005):
    stock_data = stock_data.copy()
    stock_data['bullish_fvg'] = False
    stock_data['bearish_fvg'] = False

    for i in range(2, len(stock_data)):
        c1, c2, c3 = stock_data.iloc[i-2], stock_data.iloc[i-1], stock_data.iloc[i]

        # FVG de Alta
        if (c1_high := c1['high_price']) < (c3_low := c3['low_price']):
            if (c3_low - c1_high) / c1_high >= threshold:
                stock_data.at[stock_data.index[i], 'bullish_fvg'] = True

        # FVG de Baixa
        if (c1_low := c1['low_price']) > (c3_high := c3['high_price']):
            if (c1_low - c3_high) / c1_low >= threshold:
                stock_data.at[stock_data.index[i], 'bearish_fvg'] = True

    # Handle NaN values and preserve types
    stock_data = stock_data.fillna(False)
    stock_data = stock_data.infer_objects()
    return stock_data[['bullish_fvg', 'bearish_fvg']]
