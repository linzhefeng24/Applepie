import os
from transport.server import serve
from backtesting.run import backtest
if __name__=='__main__':serve('quant_backtest',os.environ.get('HTTP_PORT','8119'),'/backtest',backtest)
