"""Numerical service route registration; transport and business logic stay separate."""
from api.analyze import handle as analyze
from api.backtest import handle as backtest

ROUTES = {'/analyze': analyze, '/backtest': backtest}
