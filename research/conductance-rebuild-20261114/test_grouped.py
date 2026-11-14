import numpy as np,pytest
from grouped_parameters import resolve,apply,group_key

def test_same_type_shares_bilateral_parameters():
 rows=[{'bodyId':'1','class':'motor neuron','type':'Ti flexor MN','somaSide':'LHS'},{'bodyId':'2','class':'motor neuron','type':'Ti flexor MN','somaSide':'RHS'}];key=group_key(rows[0]);o,a=resolve(rows,{key:{'excitatory_gain':1.2}});assert o[0]==o[1];assert a['1']==a['2']

def test_extreme_parameters_rejected():
 with pytest.raises(ValueError):apply(np.ones((1,17)),{0:{'Na':20.}})
 with pytest.raises(ValueError):resolve([{'bodyId':'1'}],{}, {'1':3.})


def test_verified_subtypes_are_not_collapsed():
 a={'class':'motor neuron','type':'Ti flexor MN','verified_motor_unit_subtype':'fast'}
 b={**a,'verified_motor_unit_subtype':'slow'}
 assert group_key(a)!=group_key(b)

def test_typo_in_group_is_rejected():
 with pytest.raises(KeyError):resolve([{'bodyId':'1','type':'T'}],{'nonexistent':{'Na':1.2}})
