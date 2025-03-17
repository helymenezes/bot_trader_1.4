import os
import time
from datetime import datetime
import logging
import math
import pandas as pd
from binance.client import Client
from binance.enums import *
from binance.enums import SIDE_SELL, ORDER_TYPE_STOP_LOSS_LIMIT
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

from modules.BinanceClient import BinanceClient
from modules.TraderOrder import TraderOrder
from modules.Logger import *
from modules.StrategyRunner import StrategyRunner

from strategies.moving_average_antecipation import getMovingAverageAntecipationTradeStrategy
from strategies.moving_average import getMovingAverageTradeStrategy

from indicators import Indicators

load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
secret_key = os.getenv("BINANCE_SECRET_KEY")

# ------------------------------------------------------------------
# Classe Principal
class BinanceTraderBot:

    # Parâmetros da classe
    last_trade_decision = None  
    last_buy_price = 0  
    last_sell_price = 0  
    open_orders = []
    partial_quantity_discount = 0

    tick_size: float
    step_size: float
    take_profit_index = 0

    # Construtor
    def __init__(
        self,
        stock_code,
        operation_code,
        traded_quantity,
        traded_percentage,
        candle_period,
        time_to_trade=30 * 60,
        delay_after_order=60 * 60,
        acceptable_loss_percentage=0.5,
        stop_loss_percentage=3.5,
        fallback_activated=True,
        take_profit_at_percentage=[],
        take_profit_amount_percentage=[],
        main_strategy=None,
        main_strategy_args=None,
        fallback_strategy=None,
        fallback_strategy_args=None,
    ):
        print("------------------------------------------------")
        print("🤖 Robo Trader iniciando...")

        # Configuração básica
        self.stock_code = stock_code  
        self.operation_code = operation_code  
        self.traded_quantity = traded_quantity  
        self.traded_percentage = traded_percentage  
        self.candle_period = candle_period  

        self.fallback_activated = fallback_activated  
        self.acceptable_loss_percentage = acceptable_loss_percentage / 100 
        self.stop_loss_percentage = stop_loss_percentage / 100 

        self.take_profit_at_percentage = take_profit_at_percentage 
        self.take_profit_amount_percentage = take_profit_amount_percentage 

        self.main_strategy = main_strategy 
        self.main_strategy_args = main_strategy_args 
        self.fallback_strategy = fallback_strategy 
        self.fallback_strategy_args = fallback_strategy_args 

        self.time_to_trade = time_to_trade
        self.delay_after_order = delay_after_order
        self.time_to_sleep = time_to_trade

        self.client_binance = BinanceClient(
            api_key, secret_key, sync=True, sync_interval=30000, verbose=False
        )

        self.setStepSizeAndTickSize()

        # Configurações para o Trailing Stop Loss:
        # Se o ativo subir 3% em relação ao preço de compra, ativa o trailing
        # e reposiciona o stop loss para 1% abaixo do pico.
        self.trailing_activation_percentage = 0.03  # 3% de alta para ativação
        self.trailing_gap = 0.01  # Trailing stop 1% abaixo do pico
        self.initial_stop_loss_price = None  # Será definido após a compra
        self.stop_loss_price = None  # Valor atual do stop loss (pode ser inicial ou trailing)
        self.max_price_since_buy = 0  # Pico do ativo após a compra

    # Atualiza o stop loss dinamicamente se o ativo subir 3%
    def updateTrailingStopLoss(self):
        close_price = self.stock_data["close_price"].iloc[-1]
        if self.actual_trade_position and self.last_buy_price > 0:
            # Ativa o trailing se o preço atual for pelo menos 3% acima do preço de compra
            if close_price >= self.last_buy_price * (1 + self.trailing_activation_percentage):
                if close_price > self.max_price_since_buy:
                    self.max_price_since_buy = close_price
                    new_trailing_stop = self.max_price_since_buy * (1 - self.trailing_gap)
                    if new_trailing_stop > self.stop_loss_price:
                        self.stop_loss_price = new_trailing_stop
                        print(f"🔄 Trailing Stop Loss ajustado para: {self.stop_loss_price:.4f}")

    # Função unificada de Stop Loss (usa o valor atual de self.stop_loss_price)
    def stopLossTrigger(self):
        close_price = self.stock_data["close_price"].iloc[-1]
        if self.actual_trade_position and close_price < self.stop_loss_price:
            print("🔴 Stop Loss acionado!")
            self.cancelAllOrders()
            time.sleep(2)
            self.sellMarketOrder()
            return True
        return False

    # Atualiza todos os dados e, se estiver comprado, define o stop loss inicial
    def updateAllData(self, verbose=False):
        try:
            self.account_data = self.getUpdatedAccountData()
            self.last_stock_account_balance = self.getLastStockAccountBalance()
            self.actual_trade_position = self.getActualTradePosition()
            self.stock_data = self.getStockData()
            self.open_orders = self.getOpenOrders()
            self.last_buy_price = self.getLastBuyPrice(verbose)
            self.last_sell_price = self.getLastSellPrice(verbose)
            if self.actual_trade_position == False:
                self.take_profit_index = 0
            # Se estiver comprado e ainda não definido, configura o stop loss inicial
            if self.actual_trade_position and self.last_buy_price > 0 and self.initial_stop_loss_price is None:
                self.initial_stop_loss_price = self.last_buy_price * (1 - self.stop_loss_percentage)
                self.stop_loss_price = self.initial_stop_loss_price
                self.max_price_since_buy = self.last_buy_price
                print(f"🔄 Stop Loss inicial definido para: {self.stop_loss_price:.4f}")
        except BinanceAPIException as e:
            print(f"Erro na atualização de dados: {e}")

    def getUpdatedAccountData(self):
        return self.client_binance.get_account()

    def getLastStockAccountBalance(self):
        in_wallet_amount = 0
        for stock in self.account_data["balances"]:
            if stock["asset"] == self.stock_code:
                free = float(stock["free"])
                locked = float(stock["locked"])
                in_wallet_amount = free + locked
        return float(in_wallet_amount)

    def getActualTradePosition(self):
        try:
            if self.last_stock_account_balance >= self.step_size:
                return True
            else:
                return False
        except Exception as e:
            print(f"Erro ao determinar a posição atual para {self.operation_code}: {e}")
            return False

    def getStockData(self):
        candles = self.client_binance.get_klines(
            symbol=self.operation_code,
            interval=self.candle_period,
            limit=1000,
        )
        prices = pd.DataFrame(candles)
        prices.columns = [
            "open_time",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "-",
        ]
        prices = prices[["close_price", "open_time", "open_price", "high_price", "low_price", "volume"]]
        prices["close_price"] = pd.to_numeric(prices["close_price"], errors="coerce")
        prices["open_price"] = pd.to_numeric(prices["open_price"], errors="coerce")
        prices["high_price"] = pd.to_numeric(prices["high_price"], errors="coerce")
        prices["low_price"] = pd.to_numeric(prices["low_price"], errors="coerce")
        prices["volume"] = pd.to_numeric(prices["volume"], errors="coerce")
        prices["open_time"] = pd.to_datetime(prices["open_time"], unit="ms").dt.tz_localize("UTC")
        prices["open_time"] = prices["open_time"].dt.tz_convert("America/Sao_Paulo")
        return prices

    def getLastBuyPrice(self, verbose=False):
        try:
            all_orders = self.client_binance.get_all_orders(
                symbol=self.operation_code,
                limit=100,
            )
            executed_buy_orders = [order for order in all_orders if order["side"] == "BUY" and order["status"] == "FILLED"]
            if executed_buy_orders:
                last_executed_order = sorted(executed_buy_orders, key=lambda x: x["time"], reverse=True)[0]
                last_buy_price = float(last_executed_order["cummulativeQuoteQty"]) / float(last_executed_order["executedQty"])
                datetime_transact = datetime.utcfromtimestamp(last_executed_order["time"] / 1000).strftime("(%H:%M:%S) %d-%m-%Y")
                if verbose:
                    print(f"\nÚltima ordem de COMPRA executada para {self.operation_code}:")
                    print(f" - Data: {datetime_transact} | Preço: {self.adjust_to_step(last_buy_price,self.tick_size, as_string=True)}")
                return last_buy_price
            else:
                if verbose:
                    print(f"Não há ordens de COMPRA executadas para {self.operation_code}.")
                return 0.0
        except Exception as e:
            if verbose:
                print(f"Erro ao verificar a última ordem de COMPRA para {self.operation_code}: {e}")
            return 0.0

    def getLastSellPrice(self, verbose=False):
        try:
            all_orders = self.client_binance.get_all_orders(
                symbol=self.operation_code,
                limit=100,
            )
            executed_sell_orders = [order for order in all_orders if order["side"] == "SELL" and order["status"] == "FILLED"]
            if executed_sell_orders:
                last_executed_order = sorted(executed_sell_orders, key=lambda x: x["time"], reverse=True)[0]
                last_sell_price = float(last_executed_order["cummulativeQuoteQty"]) / float(last_executed_order["executedQty"])
                datetime_transact = datetime.utcfromtimestamp(last_executed_order["time"] / 1000).strftime("(%H:%M:%S) %d-%m-%Y")
                if verbose:
                    print(f"Última ordem de VENDA executada para {self.operation_code}:")
                    print(f" - Data: {datetime_transact} | Preço: {self.adjust_to_step(last_sell_price,self.tick_size, as_string=True)}")
                return last_sell_price
            else:
                if verbose:
                    print(f"Não há ordens de VENDA executadas para {self.operation_code}.")
                return 0.0
        except Exception as e:
            if verbose:
                print(f"Erro ao verificar a última ordem de VENDA para {self.operation_code}: {e}")
            return 0.0

    def getTimestamp(self):
        try:
            if not hasattr(self, "time_offset") or self.time_offset is None:
                server_time = self.client_binance.get_server_time()["serverTime"]
                local_time = int(time.time() * 1000)
                self.time_offset = server_time - local_time
            adjusted_timestamp = int(time.time() * 1000) + self.time_offset
            return adjusted_timestamp
        except Exception as e:
            print(f"Erro ao ajustar o timestamp: {e}")
            return int(time.time() * 1000)

    def setStepSizeAndTickSize(self):
        symbol_info = self.client_binance.get_symbol_info(self.operation_code)
        price_filter = next(f for f in symbol_info["filters"] if f["filterType"] == "PRICE_FILTER")
        self.tick_size = float(price_filter["tickSize"])
        lot_size_filter = next(f for f in symbol_info["filters"] if f["filterType"] == "LOT_SIZE")
        self.step_size = float(lot_size_filter["stepSize"])

    def adjust_to_step(self, value, step, as_string=False):
        if step <= 0:
            raise ValueError("O valor de 'step' deve ser maior que zero.")
        decimal_places = (max(0, abs(int(math.floor(math.log10(step))))) if step < 1 else 0)
        adjusted_value = math.floor(value / step) * step
        adjusted_value = round(adjusted_value, decimal_places)
        if as_string:
            return f"{adjusted_value:.{decimal_places}f}"
        else:
            return adjusted_value

    def printWallet(self):
        for stock in self.account_data["balances"]:
            if float(stock["free"]) > 0:
                print(stock)

    def printStock(self):
        for stock in self.account_data["balances"]:
            if stock["asset"] == self.stock_code:
                print(stock)

    def printBrl(self):
        for stock in self.account_data["balances"]:
            if stock["asset"] == "BRL":
                print(stock)

    def printOpenOrders(self):
        if self.open_orders:
            print("-------------------------")
            print(f"Ordens abertas para {self.operation_code}:")
            for order in self.open_orders:
                to_print = (
                    f"----\nID {order['orderId']}:"
                    f"\n - Status: {getOrderStatus(order['status'])}"
                    f"\n - Side: {order['side']}"
                    f"\n - Ativo: {order['symbol']}"
                    f"\n - Preço: {order['price']}"
                    f"\n - Quantidade Original: {order['origQty']}"
                    f"\n - Quantidade Executada: {order['executedQty']}"
                    f"\n - Tipo: {order['type']}"
                )
                print(to_print)
            print("-------------------------")
        else:
            print(f"Não há ordens abertas para {self.operation_code}.")

    def getWallet(self):
        for stock in self.account_data["balances"]:
            if float(stock["free"]) > 0:
                return stock

    def getStock(self):
        for stock in self.account_data["balances"]:
            if stock["asset"] == self.stock_code:
                return stock

    def getPriceChangePercentage(self, initial_price, close_price):
        if initial_price == 0:
            raise ValueError("O initial_price não pode ser zero.")
        percentual_change = ((close_price - initial_price) / initial_price) * 100
        return percentual_change

    def buyMarketOrder(self, quantity=None):
        try:
            if not self.actual_trade_position:
                if quantity is None:
                    quantity = self.adjust_to_step(
                        self.last_stock_account_balance, self.step_size, as_string=True
                    )
                else:
                    quantity = self.adjust_to_step(quantity, self.step_size, as_string=True)
                order_buy = self.client_binance.create_order(
                    symbol=self.operation_code,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity,
                )
                self.actual_trade_position = True
                createLogOrder(order_buy)
                print(f"\nOrdem de COMPRA a mercado enviada com sucesso:")
                print(order_buy)
                # Após a compra, define o stop loss inicial
                self.last_buy_price = float(
                    order_buy.get("fills", [{}])[0].get("price", 0)
                ) if order_buy.get("fills") else self.getLastBuyPrice()
                self.initial_stop_loss_price = self.last_buy_price * (1 - self.stop_loss_percentage)
                self.stop_loss_price = self.initial_stop_loss_price
                self.max_price_since_buy = self.last_buy_price
                print(f"🔄 Stop Loss inicial definido para: {self.stop_loss_price:.4f}")
                return order_buy
            else:
                logging.warning("Erro ao comprar: Posição já comprada.")
                print("\nErro ao comprar: Posição já comprada.")
                return False
        except Exception as e:
            logging.error(f"Erro ao executar ordem de compra a mercado: {e}")
            print(f"\nErro ao executar ordem de compra a mercado: {e}")
            return False

    def buyLimitedOrder(self, price=0):
        close_price = self.stock_data["close_price"].iloc[-1]
        volume = self.stock_data["volume"].iloc[-1]
        avg_volume = self.stock_data["volume"].rolling(window=20).mean().iloc[-1]
        rsi = Indicators.getRSI(series=self.stock_data["close_price"])
        if price == 0:
            if rsi < 30:
                limit_price = close_price - (0.002 * close_price)
            elif volume < avg_volume:
                limit_price = close_price + (0.002 * close_price)
            else:
                limit_price = close_price + (0.005 * close_price)
        else:
            limit_price = price
        limit_price = self.adjust_to_step(limit_price, self.tick_size, as_string=True)
        quantity = self.adjust_to_step(
            self.traded_quantity - self.partial_quantity_discount, self.step_size, as_string=True
        )
        print(f"Enviando ordem limitada de COMPRA para {self.operation_code}:")
        print(f" - RSI: {rsi}")
        print(f" - Quantidade: {quantity}")
        print(f" - Close Price: {close_price}")
        print(f" - Preço Limite: {limit_price}")
        try:
            order_buy = self.client_binance.create_order(
                symbol=self.operation_code,
                side=SIDE_BUY,
                type=ORDER_TYPE_LIMIT,
                timeInForce="GTC",
                quantity=quantity,
                price=limit_price,
            )
            self.actual_trade_position = True
            print(f"\nOrdem COMPRA limitada enviada com sucesso:")
            if order_buy is not None:
                createLogOrder(order_buy)
            self.last_buy_price = float(
                order_buy.get("fills", [{}])[0].get("price", 0)
            ) if order_buy.get("fills") else self.getLastBuyPrice()
            self.initial_stop_loss_price = self.last_buy_price * (1 - self.stop_loss_percentage)
            self.stop_loss_price = self.initial_stop_loss_price
            self.max_price_since_buy = self.last_buy_price
            print(f"🔄 Stop Loss inicial definido para: {self.stop_loss_price:.4f}")
            return order_buy
        except Exception as e:
            logging.error(f"Erro ao enviar ordem limitada de COMPRA: {e}")
            print(f"\nErro ao enviar ordem limitada de COMPRA: {e}")
            return False

    def sellMarketOrder(self, quantity=None):
        try:
            if self.actual_trade_position:
                if quantity is None:
                    quantity = self.adjust_to_step(
                        self.last_stock_account_balance, self.step_size, as_string=True
                    )
                else:
                    quantity = self.adjust_to_step(quantity, self.step_size, as_string=True)
                order_sell = self.client_binance.create_order(
                    symbol=self.operation_code,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity,
                )
                self.actual_trade_position = False
                createLogOrder(order_sell)
                print(f"\nOrdem de VENDA a mercado enviada com sucesso:")
                self.max_price_since_buy = 0  # Reseta o pico
                print("🔄 Trailing Stop Loss resetado.")
                return order_sell
            else:
                logging.warning("Erro ao vender: Posição já vendida.")
                print("\nErro ao vender: Posição já vendida.")
                return False
        except Exception as e:
            logging.error(f"Erro ao executar ordem de venda a mercado: {e}")
            print(f"\nErro ao executar ordem de venda a mercado: {e}")
            return False

    def sellLimitedOrder(self, price=0):
        close_price = self.stock_data["close_price"].iloc[-1]
        volume = self.stock_data["volume"].iloc[-1]
        avg_volume = self.stock_data["volume"].rolling(window=20).mean().iloc[-1]
        rsi = Indicators.getRSI(series=self.stock_data["close_price"])
        if price == 0:
            if rsi > 70:
                limit_price = close_price + (0.002 * close_price)
            elif volume < avg_volume:
                limit_price = close_price - (0.002 * close_price)
            else:
                limit_price = close_price - (0.005 * close_price)
            if limit_price < (self.last_buy_price * (1 - self.acceptable_loss_percentage)):
                print(f"\nAjuste de venda aceitável ({self.acceptable_loss_percentage*100}%):")
                print(f" - De: {limit_price:.4f}")
                limit_price = self.getMinimumPriceToSell()
                print(f" - Para: {limit_price}")
        else:
            limit_price = price
        limit_price = self.adjust_to_step(limit_price, self.tick_size, as_string=True)
        quantity = self.adjust_to_step(
            self.last_stock_account_balance, self.step_size, as_string=True
        )
        print(f"\nEnviando ordem limitada de VENDA para {self.operation_code}:")
        print(f" - RSI: {rsi}")
        print(f" - Quantidade: {quantity}")
        print(f" - Close Price: {close_price}")
        print(f" - Preço Limite: {limit_price}")
        try:
            order_sell = self.client_binance.create_order(
                symbol=self.operation_code,
                side=SIDE_SELL,
                type=ORDER_TYPE_LIMIT,
                timeInForce="GTC",
                quantity=quantity,
                price=limit_price,
            )
            self.actual_trade_position = False
            print(f"\nOrdem VENDA limitada enviada com sucesso:")
            createLogOrder(order_sell)
            return order_sell
        except Exception as e:
            logging.error(f"Erro ao enviar ordem limitada de VENDA: {e}")
            print(f"\nErro ao enviar ordem limitada de VENDA: {e}")
            return False

    def getOpenOrders(self):
        open_orders = self.client_binance.get_open_orders(symbol=self.operation_code)
        return open_orders

    def cancelOrderById(self, order_id):
        self.client_binance.cancel_order(symbol=self.operation_code, orderId=order_id)

    def cancelAllOrders(self):
        if self.open_orders:
            for order in self.open_orders:
                try:
                    self.client_binance.cancel_order(symbol=self.operation_code, orderId=order["orderId"])
                    print(f"❌ Ordem {order['orderId']} cancelada.")
                except Exception as e:
                    print(f"Erro ao cancelar ordem {order['orderId']}: {e}")

    def hasOpenBuyOrder(self):
        self.partial_quantity_discount = 0.0
        try:
            open_orders = self.client_binance.get_open_orders(symbol=self.operation_code)
            buy_orders = [order for order in open_orders if order["side"] == "BUY"]
            if buy_orders:
                self.last_buy_price = 0.0
                print(f"\nOrdens de compra abertas para {self.operation_code}:")
                for order in buy_orders:
                    executed_qty = float(order["executedQty"])
                    price = float(order["price"])
                    print(f" - ID da Ordem: {order['orderId']}, Preço: {price}, Qnt.: {order['origQty']}, Qnt. Executada: {executed_qty}")
                    self.partial_quantity_discount += executed_qty
                    if executed_qty > 0 and price > self.last_buy_price:
                        self.last_buy_price = price
                print(f" - Quantidade parcial executada no total: {self.partial_quantity_discount}")
                print(f" - Maior preço parcialmente executado: {self.last_buy_price}")
                return True
            else:
                print(f" - Não há ordens de compra abertas para {self.operation_code}.")
                return False
        except Exception as e:
            print(f"Erro ao verificar ordens abertas para {self.operation_code}: {e}")
            return False

    def hasOpenSellOrder(self):
        self.partial_quantity_discount = 0.0
        try:
            open_orders = self.client_binance.get_open_orders(symbol=self.operation_code)
            sell_orders = [order for order in open_orders if order["side"] == "SELL"]
            if sell_orders:
                print(f"\nOrdens de venda abertas para {self.operation_code}:")
                for order in sell_orders:
                    executed_qty = float(order["executedQty"])
                    print(f" - ID da Ordem: {order['orderId']}, Preço: {order['price']}, Qnt.: {order['origQty']}, Qnt. Executada: {executed_qty}")
                    self.partial_quantity_discount += executed_qty
                print(f" - Quantidade parcial executada no total: {self.partial_quantity_discount}")
                return True
            else:
                print(f" - Não há ordens de venda abertas para {self.operation_code}.")
                return False
        except Exception as e:
            print(f"Erro ao verificar ordens abertas para {self.operation_code}: {e}")
            return False

    def getFinalDecisionStrategy(self):
        final_decision = StrategyRunner.execute(
            self,
            stock_data=self.stock_data,
            main_strategy=self.main_strategy,
            main_strategy_args=self.main_strategy_args,
            fallback_strategy=self.fallback_strategy,
            fallback_strategy_args=self.fallback_strategy_args,
        )
        return final_decision

    def getMinimumPriceToSell(self):
        return self.last_buy_price * (1 - self.acceptable_loss_percentage)

    def takeProfitTrigger(self):
        try:
            close_price = self.stock_data["close_price"].iloc[-1]
            price_percentage_variation = self.getPriceChangePercentage(
                initial_price=self.last_buy_price, close_price=close_price
            )
            print(f" - Variação atual: {price_percentage_variation:.2f}%")
            if self.take_profit_index < len(self.take_profit_at_percentage):
                tp_percentage = self.take_profit_at_percentage[self.take_profit_index]
                tp_amount = self.take_profit_amount_percentage[self.take_profit_index]
                print(f" - Próxima meta Take Profit: {tp_percentage}% (Venda de: {tp_amount}%)\n")
                if (
                    self.actual_trade_position
                    and tp_percentage > 0
                    and round(price_percentage_variation, 2) >= round(tp_percentage, 2)
                ):
                    quantity_to_sell = self.last_stock_account_balance * (tp_amount / 100)
                    if quantity_to_sell > 0:
                        log = (
                            f"🎯 Meta de Take Profit atingida! ({tp_percentage}% lucro)\n"
                            f" - Vendendo {tp_amount}% da carteira...\n"
                            f" - Preço atual: {close_price:.4f}\n"
                            f" - Quantidade vendida: {quantity_to_sell:.6f} {self.stock_code}"
                        )
                        print(log)
                        logging.info(log)
                        order_result = self.sellMarketOrder(quantity=quantity_to_sell)
                        if order_result:
                            self.take_profit_index += 1
                            return True
            return False
        except Exception as e:
            print(f"Erro no takeProfitTrigger: {e}")
            return False

    # Método principal execute - Implementação completa do ciclo de negociação
    def execute(self):
        """
        Executa o ciclo principal de negociação do bot.
        """
        try:
            print(f"\n🔍 Analisando {self.operation_code}...")
            
            # Atualiza todos os dados necessários (preços, saldos, posições)
            self.updateAllData(verbose=True)
            
            # Verifica se há ordens abertas
            has_buy_orders = self.hasOpenBuyOrder()
            has_sell_orders = self.hasOpenSellOrder()

            # Se estiver em uma posição comprada, verifica stop loss e take profit
            if self.actual_trade_position:
                # Atualiza o trailing stop loss se necessário
                self.updateTrailingStopLoss()
                
                # Verifica se o stop loss foi acionado
                if self.stopLossTrigger():
                    self.time_to_sleep = self.delay_after_order
                    return
                
                # Verifica se o take profit foi acionado
                if self.takeProfitTrigger():
                    self.time_to_sleep = self.delay_after_order
                    return
            
            # Se não houver ordens abertas, executa a estratégia para decidir o próximo movimento
            if not has_buy_orders and not has_sell_orders:
                trade_decision = self.getFinalDecisionStrategy()
                
                # Se houver um sinal de COMPRA e não estiver em posição comprada
                if trade_decision == True and not self.actual_trade_position:
                    print("🟢 Sinal de COMPRA detectado!")
                    self.buyMarketOrder()
                    self.time_to_sleep = self.delay_after_order
                    return
                
                # Se houver um sinal de VENDA e estiver em posição comprada
                elif trade_decision == False and self.actual_trade_position:
                    print("🔴 Sinal de VENDA detectado!")
                    self.sellMarketOrder()
                    self.time_to_sleep = self.delay_after_order
                    return
                
                else:
                    print("⚪ Nenhum sinal de negociação detectado.")
                    self.time_to_sleep = self.time_to_trade
            else:
                print(f"⏳ Aguardando execução das ordens abertas para {self.operation_code}...")
                self.time_to_sleep = self.time_to_trade / 2  # Reduz o tempo para verificar mais rápido
            
        except Exception as e:
            logging.error(f"Erro durante a execução do ciclo de negociação: {e}")
            print(f"❌ Erro: {e}")
            self.time_to_sleep = self.time_to_trade
            
        return
