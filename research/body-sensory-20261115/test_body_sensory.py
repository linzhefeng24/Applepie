import json
from pathlib import Path
import numpy as np
from body_sensory import transduce,leg_of

def test_unloaded_feet_have_no_load_or_touch_input_and_velocity_channels_separate():
 p=json.load(open(Path(__file__).with_name('parameters.json')));q=np.full((2,6),p['neutral_knee_deg']);v=np.ones_like(q)*100;v[1]*=-1
 r=transduce(dict(knee_deg=q,knee_velocity_deg_s=v,load_bodyweights=np.zeros_like(q),foot_load_bodyweights=np.zeros_like(q)),p)
 assert not r['load_current_pA'].any() and not r['touch_current_pA'].any();assert not r['proprio_current_pA'][0,:,0].any();assert not r['proprio_current_pA'][1,:,1].any();assert not r['proprio_current_pA'][:,:,2:].any()

def test_load_current_is_monotone_bounded_and_not_a_joint_angle_proxy():
 p=json.load(open(Path(__file__).with_name('parameters.json')));load=np.array([0,.01,.05,.2,1.,10.]);r=transduce(dict(knee_deg=np.full(6,p['neutral_knee_deg']),knee_velocity_deg_s=np.zeros(6),load_bodyweights=load,foot_load_bodyweights=load),p)
 assert np.all(np.diff(r['load_current_pA'])>0);assert max(r['load_current_pA'])<p['load_max_pA'];assert not r['proprio_current_pA'].any();assert leg_of('walker/tarsal_claw_T3_right_collision')=='RH';assert leg_of('groundplane') is None

def test_force_calibration_stays_fixed_when_environment_gravity_changes():
 p=json.load(open(Path(__file__).with_name('parameters.json')));m=dict(knee_deg=np.zeros(6),knee_velocity_deg_s=np.zeros(6),load_bodyweights=np.ones(6),foot_load_bodyweights=np.ones(6),ground_normal_native=np.full(6,.3),foot_normal_native=np.full(6,.2));a=transduce(m,p);m['load_bodyweights']*=2;m['foot_load_bodyweights']*=2;b=transduce(m,p);np.testing.assert_array_equal(a['load_current_pA'],b['load_current_pA']);np.testing.assert_array_equal(a['touch_current_pA'],b['touch_current_pA'])
