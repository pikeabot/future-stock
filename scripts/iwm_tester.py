from ..backtesterclass import BacktesterClass
from ..backtester.scriptclass import ScriptClass

script = ScriptClass(10000, 5, 5, 'IWM')
backtester = BacktesterClass(script)
backtester.run()