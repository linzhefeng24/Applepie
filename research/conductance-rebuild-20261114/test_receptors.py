import numpy as np,pytest
from network import receptor_conductances,simulate_network

def metadata():
 return [dict(bodyId=str(i),type=t,**{'class':'intrinsic_neuron'},connectome_namespace='test',predictedNt=nt) for i,t,nt in [(0,'G','gaba'),(1,'target','acetylcholine'),(2,'Gl','glutamate')]]
KEY='test|intrinsic_neuron|type:target'

def test_receptor_intervention_preserves_structural_counts_and_other_transmitters():
 w=np.array([[0.,-2,0],[3,0,0],[0,-4,0]]);original=w.copy();x,record=receptor_conductances(w,metadata(),{KEY:{'GABAA':2.}})
 np.testing.assert_array_equal(w,original);assert x[0,1]==-4 and x[2,1]==-4 and x[1,0]==3;assert record[0]['receptors']['GABAA']['affected_negative_edges']==1

def test_receptor_namespace_and_range_are_validated():
 with pytest.raises(KeyError):receptor_conductances(np.zeros((3,3)),metadata(),{'other|intrinsic_neuron|type:target':{'GABAA':2.}})
 with pytest.raises(ValueError):receptor_conductances(np.zeros((3,3)),metadata(),{KEY:{'GABAA':-1.}})

def test_gabaa_block_keeps_glutamate_inhibition():
 w=np.zeros((3,3));w[0,1]=-2;w[2,1]=-4;x,_=receptor_conductances(w,metadata(),{KEY:{'GABAA':0.}});assert x[0,1]==0 and x[2,1]==-4

def test_no_feedback_source_spikes_unchanged_and_target_conductance_scales():
 w=np.zeros((3,3));w[0,1]=w[2,1]=-20;p={'duration_ms':120.,'onset_ms':10.,'dt_ms':.025};drive=np.array([160.,0.,160.]);a=simulate_network(w,['other']*3,metadata(),p,drive=drive,record_indices=[1]);b=simulate_network(w,['other']*3,metadata(),{**p,'target_receptor_gains':{KEY:{'GABAA':2.}}},drive=drive,record_indices=[1]);np.testing.assert_array_equal(a['spike_counts_1ms'][:,[0,2]],b['spike_counts_1ms'][:,[0,2]]);assert a['spike_counts_1ms'][:,0].sum()>0
 np.testing.assert_allclose(b['synaptic_conductances_nS'][:,:,1],1.5*a['synaptic_conductances_nS'][:,:,1],rtol=1e-12,atol=1e-12)

def test_type_pair_gain_is_namespace_specific_and_preserves_all_edges():
 from network import type_pair_conductances
 rows=metadata();w=np.zeros((3,3));w[0,1]=2.;w[2,1]=-4.;w[0,2]=3.;x,r=type_pair_conductances(w,rows,[{'namespace':'test','source_type':'G','target_type':'target','gain':.2}]);assert x[0,1]==.4 and x[2,1]==-4 and x[0,2]==3 and w[0,1]==2;np.testing.assert_array_equal(x!=0,w!=0);assert r[0]['affected_existing_edges']==1
 with pytest.raises(ValueError):type_pair_conductances(w,rows,[{'namespace':'test','source_type':'G','target_type':'target','gain':0.}])
 with pytest.raises(KeyError):type_pair_conductances(w,rows,[{'namespace':'other','source_type':'G','target_type':'target','gain':.2}])
