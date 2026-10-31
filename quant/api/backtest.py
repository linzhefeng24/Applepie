"""Pure request handler for the numerical backtest API."""
from engine import backtest

def handle(payload):
    return backtest(payload)
