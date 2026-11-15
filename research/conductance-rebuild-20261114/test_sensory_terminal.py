import json,numpy as np,pytest
from pathlib import Path
from sensory_terminal_model import solve_cable,simulate

def config():
 p=json.load(open(Path(__file__).parent/'configs/sensory-terminal-prototype.json'));p.update(duration_ms=160.,movement_start_ms=20.,movement_end_ms=150.,movement_period_ms=200.);return p

def test_three_compartment_cable_matches_linear_current_balance():
 d=np.array([24.,35.,18.]);k01=3.;k12=2.;rhs=np.array([-1300.,-1700.,-1000.]);A=np.diag(d);A[0,1]=A[1,0]=-k01;A[1,2]=A[2,1]=-k12;np.testing.assert_allclose(solve_cable(d,rhs,k01,k12),np.linalg.solve(A,rhs),rtol=1e-13)

def test_gabaa_block_restores_transmission_and_claw_is_not_targeted():
 p=config();source=np.zeros(160);source[10::20]=1;a=simulate(np.zeros(160),p);b=simulate(source,p);c=simulate(source,{**p,'chief_compound_peak_nS':0.});assert not a['numerical_failure'] and not b['numerical_failure'];np.testing.assert_array_equal(a['voltage'],c['voltage']);np.testing.assert_array_equal(a['voltage'][:,2:],b['voltage'][:,2:]);assert b['gaba_nS'].max()>0;assert np.any(a['voltage'][:,:2]!=b['voltage'][:,:2])

def test_passive_membrane_does_not_spike_without_mechanical_drive():
 p=config();p.update(claw_current_pA_per_deg=0.,hook_current_pA_per_deg_s=0.);r=simulate(np.zeros(160),p);assert not r['spikes'].any();assert np.isfinite(r['voltage']).all()

def test_invalid_spike_input_and_geometry_rejected():
 with pytest.raises(ValueError):simulate(np.array([-1.]),config())
 with pytest.raises(ValueError):simulate(np.zeros(160),{**config(),'capacitance_pF':[1.]})
