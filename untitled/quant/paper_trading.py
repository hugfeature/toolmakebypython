import backtrader as bt

class MovingAverageStrategy(bt.Strategy):
    params = (('sma1', 10), ('sma2', 50), ('stop_loss', 0.95), ('take_profit', 1.10))

    def __init__(self):
        self.sma1 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma1)
        self.sma2 = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma2)
        self.buy_price = None  # 记录买入价格

    def next(self):
        if not self.position:  # 只有在没有持仓时才寻找买入机会
            if self.sma1[0] > self.sma2[0] and self.sma1[-1] <= self.sma2[-1]:
                self.buy_price = self.data.close[0]  # 记录买入价格
                self.buy()
        else:
            # 当前价格
            current_price = self.data.close[0]
            
            # 止盈：当前价格 >= 买入价格 * 1.10 (10% 收益)
            if current_price >= self.buy_price * self.params.take_profit:
                self.sell()
                self.buy_price = None  # 清空买入价格

            # 止损：当前价格 <= 买入价格 * 0.95 (5% 亏损)
            elif current_price <= self.buy_price * self.params.stop_loss:
                self.sell()
                self.buy_price = None  # 清空买入价格
cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)
cerebro.addstrategy(MovingAverageStrategy, stop_loss=0.95, take_profit=1.10)

# 设定初始资金
cerebro.broker.set_cash(10000)
cerebro.broker.setcommission(commission=0.001)

# 运行回测
cerebro.run()
cerebro.plot()