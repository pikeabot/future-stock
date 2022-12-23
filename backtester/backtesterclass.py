from backtester.utils import get_equity_data

class BacktesterClass:

    def __init__(self, script_class):
        self.script_class = script_class

    def run(self):
        data = get_equity_data(self.script_class.equity)
        print(data)

    def daily_profit_loss(self):
        pass

    def daily_risk(self):
        pass
