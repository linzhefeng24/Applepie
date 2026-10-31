import unittest
from unittest.mock import patch
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from engine import statistics,optimize,simulate,align,validate,capped_simplex,analyze
P=dict(symbols=['A','B','C'],start='2020-01-01',end='2024-01-01',maxWeight=.6,riskAversion=3,skewPreference=1,kurtosisAversion=1,lookback=60,rebalance=21,costBps=10,model='mvsk')
class EngineTests(unittest.TestCase):
 def test_statistics_includes_initial_capital_in_drawdown(self):
  m=statistics([-.1,.1]);self.assertAlmostEqual(m['maxDrawdown'],-.1);self.assertAlmostEqual(m['totalReturn'],-.01)
 def test_statistics_four_moments(self):
  r=np.array([-.1,-.01,.02,.03,.08]);m=statistics(r);c=r-r.mean();self.assertAlmostEqual(m['skewness'],np.mean(c**3)/np.mean(c**2)**1.5);self.assertAlmostEqual(m['excessKurtosis'],np.mean(c**4)/np.mean(c**2)**2-3)
 def test_all_models_long_only_capped(self):
  r=np.random.default_rng(12).normal([.001,.0002,.0003],[.02,.008,.013],(300,3))
  for model in ['equal','minvariance','meanvariance','mvsk','riskparity']:
   with self.subTest(model=model):
    a=optimize(r,model,P);w=np.array(a['weights']);self.assertTrue(a['converged']);self.assertAlmostEqual(w.sum(),1);self.assertGreaterEqual(w.min(),-1e-8);self.assertLessEqual(w.max(),.600001)
  w=np.array(optimize(r,'minvariance',P)['weights']);self.assertLessEqual(np.var(r@w),np.var(r@np.ones(3)/3)+1e-8)
 def test_infeasible_constraints_rejected(self):
  with self.assertRaises(ValueError):validate(dict(P,maxWeight=.2))
  with self.assertRaises(ValueError):validate(dict(P,costBps=-1))
 def test_projection_capped_simplex(self):
  w=capped_simplex(np.array([5.,-2.,.8]),.4);self.assertAlmostEqual(w.sum(),1);self.assertLessEqual(w.max(),.4);self.assertGreaterEqual(w.min(),0)
 def test_missing_prices_are_not_forward_filled(self):
  dates=[f'2020-{1+i//28:02d}-{1+i%28:02d}' for i in range(65)]
  series={s:[dict(date=d,close=100+i) for i,d in enumerate(dates) if s!='B' or i!=10] for s in ['A','B']}
  d,r,dropped=align(series,['A','B']);self.assertNotIn(dates[10],d);self.assertEqual(dropped['A'],1);self.assertAlmostEqual(r[9,0],111/109-1)
 def test_signal_lag_and_training_window(self):
  r=np.random.default_rng(1).normal(0,.01,(100,3));dates=[f'{i:04d}' for i in range(101)];calls=[]
  def capture(sample,*args):calls.append(sample.copy());return dict(weights=[1/3]*3,converged=True)
  with patch('engine.optimize',side_effect=capture):out=simulate(r,dates,'equal',P)
  np.testing.assert_array_equal(calls[0],r[:60]);t=out['trades'][0];self.assertLess(t['signalEnd'],t['executionDate']);self.assertLess(t['executionDate'],t['returnDate']);self.assertEqual(t['signalEnd'],dates[60]);self.assertEqual(t['executionDate'],dates[61])
 def test_future_changes_do_not_change_prior_backtest(self):
  r=np.random.default_rng(2).normal(0,.01,(130,3));dates=[f'{i:04d}' for i in range(131)];a=simulate(r,dates,'minvariance',P);changed=r.copy();changed[100:]=.2; b=simulate(changed,dates,'minvariance',P)
  self.assertEqual(a['curve'][:40],b['curve'][:40]);self.assertEqual(a['trades'][:2],b['trades'][:2])
 def test_initial_cash_entry_fee(self):
  r=np.zeros((100,3));dates=[str(i) for i in range(101)];out=simulate(r,dates,'equal',P);self.assertAlmostEqual(out['curve'][-1]['value'],.999);self.assertAlmostEqual(out['trades'][0]['turnover'],1);self.assertAlmostEqual(out['totalTurnover'],1)
 def test_weights_drift_between_rebalances(self):
  r=np.zeros((90,3));r[61,0]=.3;r[62,0]=.3;dates=[str(i) for i in range(91)];p=dict(P,costBps=0);out=simulate(r,dates,'equal',p)
  # Buy and hold first two days: initial thirds become (1.69 + 1 + 1)/3.
  self.assertAlmostEqual(out['curve'][2]['value'],3.69/3)
 def test_trading_costs_reduce_net_equity(self):
  r=np.random.default_rng(5).normal(0,.01,(130,3));dates=[str(i) for i in range(131)];a=simulate(r,dates,'equal',dict(P,costBps=0));b=simulate(r,dates,'equal',dict(P,costBps=30));self.assertGreater(a['curve'][-1]['value'],b['curve'][-1]['value'])
 def test_same_returns_deterministic_solver(self):
  r=np.random.default_rng(7).normal(0,.01,(120,3));self.assertEqual(optimize(r,'mvsk',P),optimize(r,'mvsk',P))
if __name__=='__main__':unittest.main(verbosity=2)
