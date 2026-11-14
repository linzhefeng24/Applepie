"""Protect old simulations and pulse alignment when enabling real assays."""
import numpy as np,pytest
from model import simulate
from grouped_parameters import resolve,apply

def test_step_protocol_matches_original_constant_drive():
 p={'duration_ms':100.,'onset_ms':20.,'dt_ms':.0125};w=np.zeros((1,1));wave=np.zeros((100,1));wave[20:]=160
 a=simulate(w,['DN'],p);b=simulate(w,['DN'],p,drive_waveform=wave)
 np.testing.assert_array_equal(a['spike_counts_1ms'],b['spike_counts_1ms']);np.testing.assert_array_equal(a['voltage_first12'],b['voltage_first12']);np.testing.assert_array_equal(a['calcium_first12_uM'],b['calcium_first12_uM'])

def test_malformed_protocol_rejected():
 with pytest.raises(ValueError):simulate(np.zeros((1,1)),['DN'],drive_waveform=np.zeros((100,2)))
 with pytest.raises(ValueError):simulate(np.zeros((1,1)),['DN'],{'input_sample_ms':0})

def test_absolute_calcium_prior_and_type_sharing():
 rows=[{'bodyId':'1','class':'intrinsic neuron','type':'X'},{'bodyId':'2','class':'intrinsic neuron','type':'X'}];ov,_=resolve(rows,{'intrinsic neuron|type:X':{'calcium_tau_ms':850.}});c=apply(np.ones((2,17)),ov);assert c[0,16]==c[1,16]==850.
 with pytest.raises(ValueError):apply(np.ones((1,17)),{0:{'calcium_tau_ms':10000}})
