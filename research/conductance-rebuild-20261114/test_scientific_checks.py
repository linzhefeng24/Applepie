"""Independent source, numerical and physiological acceptance checks."""
from pathlib import Path
import json,numpy as np
from model import simulate
from metrics import summarize
from muscle_readout import muscle_derivative
R=Path(__file__).parent

def test_recorded_connectivity_and_I2_are_preserved():
 z=np.load(R/'data/core.npz');np.testing.assert_array_equal(z['body_ids'],[10093,10707,11751,13905,10242]);w=z['weights'];assert w[2,4]==231 and w[4,1]==-387 and w[3,1]==-531

def test_no_imposed_clock_or_spontaneous_core_rhythm():
 z=np.load(R/'data/core.npz');p=json.load(open(R/'configs/core-selected.json'));p['drive_pA']=0.;r=simulate(z['weights'],['DN','E1','E2','I1','I2'],p);assert not r['numerical_failure'];assert r['spike_counts_1ms'][400:].sum()==0

def test_deterministic_continuous_HH_and_excitatory_necessity():
 w=np.load(R/'data/core.npz')['weights'];p=json.load(open(R/'configs/core-selected.json'));roles=['DN','E1','E2','I1','I2'];a=simulate(w,roles,p);b=simulate(w,roles,p);np.testing.assert_array_equal(a['spike_counts_1ms'],b['spike_counts_1ms']);assert np.max(abs(a['voltage_first12'][:-1,:,0]-a['voltage_first12'][:-1,:,1]))>5
 for deleted in [1,2]:
  r=simulate(w,roles,p,ablate=[deleted]);assert not any(summarize(r)['cells'][j]['rhythmic'] for j in [1,2])

def test_fine_timestep_preserves_core_frequency():
 w=np.load(R/'data/core.npz')['weights'];p=json.load(open(R/'configs/core-selected.json'));p['dt_ms']=.003125;a=summarize(simulate(w,['DN','E1','E2','I1','I2'],p));b=summarize(simulate(w,['DN','E1','E2','I1','I2'],{**p,'dt_ms':p['dt_ms']/2}))
 assert b['cells'][1]['rhythmic'];assert abs(a['cells'][1]['burst_frequency_hz']/b['cells'][1]['burst_frequency_hz']-1)<.10

def test_native_muscle_oracle():
 z=np.load(R/'data/native-muscle-derivative-check.npz');errors=[]
 for k in range(len(z['u'])):
  for j in range(130):errors.append(abs(muscle_derivative(z['u'][k,j],z['a'][k,j],*z['dynprm'][j,:2])-z['reference'][k,j]))
 assert max(errors)<1e-9

def test_adult_recruitment_order_and_rest():
 d=json.load(open(R/'results/adult-fI.json'));assert d['slow']['first_tested_current_with_rate_ge5Hz']<d['intermediate']['first_tested_current_with_rate_ge5Hz']<d['fast']['first_tested_current_with_rate_ge5Hz'];assert 25<=d['slow']['fI'][0]['rate_hz']<=35;assert d['intermediate']['fI'][0]['rate_hz']==d['fast']['fI'][0]['rate_hz']==0

def test_native_body_bridge_activation():
 d=json.load(open(R/'results/body-bridge.json'));assert len(d)==2
 for row in d:assert row['activation_bridge_max_error']<1e-8 and row['finite'] and not row['extra_applied_forces'] and row['continuous_without_state_reset']

def test_full_network_fine_step_and_E2_necessity():
 a=json.load(open(R/'results/fine-full-baseline-dt0.00625.json'));b=json.load(open(R/'results/fine-full-baseline-dt0.003125.json'));c=json.load(open(R/'results/fine-full-E2_silenced-dt0.003125.json'))
 assert abs(a['summary']['cells'][1]['burst_frequency_hz']/b['summary']['cells'][1]['burst_frequency_hz']-1)<.05
 assert b['summary']['rhythmic_MN']>0 and c['summary']['rhythmic_MN']==0
