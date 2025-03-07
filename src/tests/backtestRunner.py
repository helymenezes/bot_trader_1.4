import pandas as pd

def backtestRunner(
    stock_data: pd.DataFrame, strategy_function, strategy_instance=None, periods=900, initial_balance=1000, **strategy_kwargs
):
    """
    Executa um backtest de qualquer estratégia que segue a lógica de:
    - True = comprado
    - False = vendido

    O bot verifica se já está comprado/vendido e só age no primeiro sinal.

    :param stock_data: DataFrame contendo os dados do ativo.
    :param strategy_function: Função da estratégia de trading (ex: utBotAlerts, getMovingAverageTradeStrategy).
    :param strategy_instance: Instância da classe (ex: devTrader) para estratégias que exigem 'self'.
    :param periods: Número de períodos a serem analisados no backtest.
    :param initial_balance: Saldo inicial da conta de trading.
    :param strategy_kwargs: Parâmetros adicionais para a estratégia.
    :return: Exibe estatísticas do backtest.
    """
    # Verifica se o DataFrame tem os dados necessários
    required_columns = ['close_price']
    if not all(col in stock_data.columns for col in required_columns):
        raise ValueError(f"DataFrame deve conter as colunas: {required_columns}")
    
    if stock_data.empty:
        raise ValueError("DataFrame está vazio")
        
    if stock_data['close_price'].isnull().any():
        print("⚠️ Aviso: Existem valores nulos na coluna close_price")
        stock_data = stock_data.dropna(subset=['close_price'])

    # 🔹 Ajuste para garantir que há dados suficientes para calcular médias móveis corretamente
    min_required_periods = strategy_kwargs.get("slow_window", 40) + 20  # Adicionamos um buffer extra
    stock_data = stock_data[-max(periods, min_required_periods) :].copy().reset_index(drop=True)

    # 🔹 REMOVE LINHAS INICIAIS COM NaN PARA EVITAR PROBLEMAS
    stock_data.dropna(inplace=True)

    # Inicializa variáveis do backtest
    balance = initial_balance  # Saldo inicial
    position = 0  # 1 = comprado, -1 = vendido, 0 = sem posição
    entry_price = 0  # Preço de entrada na operação
    last_signal = None  # Guarda o último tipo de sinal para evitar compras/vendas consecutivas
    trades = 0  # Contador de operações

    print(f"📊 Iniciando backtest da estratégia: {strategy_function.__name__}")
    print(f"🔹 Balanço inicial: ${balance:.2f}")

    # Loop sobre cada período no dataset
    for i in range(1, len(stock_data)):
        current_data = stock_data.iloc[: i + 1].copy()  # Usar .copy() para evitar SettingWithCopyWarning

        try:
            # Se a função precisa de um objeto (ex: `self`), passamos a instância do bot
            if strategy_instance:
                signal = strategy_function(strategy_instance)
            else:
                signal = strategy_function(current_data, **strategy_kwargs)
        except Exception as e:
            print(f"⚠️ Erro ao executar estratégia: {str(e)}")
            continue

        # Se o sinal for `None`, pulamos para evitar erros
        if signal is None:
            continue

        close_price = stock_data.iloc[i]["close_price"]

        # Compra apenas no primeiro sinal de compra e se não estiver comprado
        if signal and position == 0 and last_signal != "buy":
            position = 1
            entry_price = close_price
            last_signal = "buy"
            trades += 1

        # Venda apenas no primeiro sinal de venda e se estiver comprado
        elif not signal and position == 1 and last_signal != "sell":
            position = 0
            profit = ((close_price - entry_price) / entry_price) * balance
            balance += profit
            last_signal = "sell"
            trades += 1

    # Fechar posição final
    if position == 1:
        final_price = stock_data.iloc[-1]["close_price"]
        profit = ((final_price - entry_price) / entry_price) * balance
        balance += profit

    # 🔹 Agora calculamos `profit_percentage` antes do `print()`
    profit_percentage = ((balance - initial_balance) / initial_balance) * 100

    # Resultados
    print(f"🔹 Balanço final: ${balance:.2f}")
    print(f"📈 Lucro/prejuízo percentual: {profit_percentage:.2f}%")
    print(f"📊 Total de operações realizadas: {trades}")

    return profit_percentage
