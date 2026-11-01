"""Compatibility exports; implementation lives in separate domain/model modules."""
from shared.constants import MODELS,LABELS,WARNINGS
from shared.validation import validate
from shared.alignment import align
from shared.statistics import statistics
from optimization.projection import capped_simplex
from optimization.objective import objective
from optimization.solver import optimize
from optimization.analysis import analyze
from backtesting.simulation import simulate
from backtesting.run import backtest
