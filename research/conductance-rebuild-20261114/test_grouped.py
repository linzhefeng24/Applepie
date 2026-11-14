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


def test_class_prototype_shares_across_types_with_explicit_override():
 rows=[{'bodyId':'1','class':'descending_neuron','type':'A'},{'bodyId':'2','class':'descending_neuron','type':'B'}]
 o,_=resolve(rows,{'descending_neuron|type:B':{'K':.9}},class_parameters={'descending neuron':{'K':.8,'axon_bias_pA':5.}})
 assert o[0]['K']==.8 and o[1]['K']==.9
 assert o[0]['axon_bias_pA']==o[1]['axon_bias_pA']==5.


def test_transmitter_family_does_not_change_inhibitory_dn_template():
 rows=[{'bodyId':'1','class':'descending_neuron','type':'X','predictedNt':'acetylcholine'},{'bodyId':'2','class':'descending_neuron','type':'Y','predictedNt':'gaba'}]
 o,_=resolve(rows,{},family_parameters={'descending neuron|NT:acetylcholine':{'K':.8}})
 assert o[0]['K']==.8 and 1 not in o


def test_individual_parameters_are_namespace_qualified():
 rows=[{'bodyId':'10462','class':'motor neuron','type':'Ti extensor MN','connectome_namespace':'MANC'},{'bodyId':'10462','class':'descending_neuron','type':'Different cell','connectome_namespace':'MaleCNS_v1.0'}]
 o,_=resolve(rows,{},cell_parameters={'MANC:10462':{'excitatory_gain':.5}})
 assert o[0]['excitatory_gain']==.5 and 1 not in o
 with pytest.raises(KeyError):resolve(rows,{},cell_parameters={'10462':{'Na':.8}})
