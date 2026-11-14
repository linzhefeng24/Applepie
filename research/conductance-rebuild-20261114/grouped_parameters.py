"""Hierarchical sharing: annotated type first, conservative fallback; no free
per-cell fitting by default. Similarity is annotation-based, not proven equality.
Bounds below are modelling priors, not physiological confidence intervals.
"""
import numpy as np
FIELDS={'capacitance_soma':0,'capacitance_axon':1,'leak_soma':2,'leak_axon':3,'E_leak_mV':4,'excitatory_gain':5,'inhibitory_gain':6,'coupling':7,'SK_scale':8,'NaP':9,'axon_bias_pA':10,'gate_speed':11,'source_gain':12,'Na':13,'K':14,'Ca':15,'calcium_tau':16}
MULTIPLIER_BOUNDS=(.5,2.)
ADDITIVE_BOUNDS={'E_leak_mV':(-5.,5.),'axon_bias_pA':(-10.,10.)}

def group_key(row):
 typ=str(row.get('type','')).strip();cl=str(row.get('class','')).strip();nt=str(row.get('predictedNt','')).strip()
 if typ and typ not in {'unknown','Unknown','TBD','SNxxxx'}:return cl+'|type:'+typ
 return cl+'|hemilineage:'+str(row.get('hemilineage','unknown'))+'|NT:'+nt

def resolve(metadata,group_parameters,individual_offsets=None):
 """Apply the same parameters to every member of a group. Individual offsets
 are additive leak shifts only, limited to±2mV, opt-in and explicitly recorded.
 No changes to structural weights, edge direction, receptor sign or stimulus.
 """
 out={};assignments={}
 for i,row in enumerate(metadata):
  key=group_key(row);assignments[str(row['bodyId'])]=key
  if key in group_parameters:out[i]=group_parameters[key]
 for bid,offset in (individual_offsets or {}).items():
  if abs(float(offset))>2:raise ValueError('Individual leak offset exceeds2mV prior')
  idx=next((i for i,x in enumerate(metadata) if str(x['bodyId'])==str(bid)),None)
  if idx is None:raise KeyError(bid)
  out[idx]={**out.get(idx,{})};old=out[idx].get('E_leak_mV',0.);out[idx]['E_leak_mV']=old+float(offset)
 return out,assignments

def apply(cell,overrides):
 cell=cell.copy()
 for idx,values in overrides.items():
  for name,value in values.items():
   if name not in FIELDS:raise KeyError(name)
   value=float(value);j=FIELDS[name]
   if not np.isfinite(value):raise ValueError('Nonfinite group parameter')
   if name in ADDITIVE_BOUNDS:
    lo,hi=ADDITIVE_BOUNDS[name]
    if not lo<=value<=hi:raise ValueError('Additive prior exceeded: '+name)
    cell[idx,j]+=value
   else:
    if not MULTIPLIER_BOUNDS[0]<=value<=MULTIPLIER_BOUNDS[1]:raise ValueError('Multiplier prior exceeded: '+name)
    cell[idx,j]*=value
 return cell

def regularization(group_parameters,individual_offsets=None):
 """Shrink toward baseline; individual offsets cost more than shared changes."""
 penalty=0.
 for values in group_parameters.values():
  for k,v in values.items():penalty+=(float(v)/5.)**2 if k in ADDITIVE_BOUNDS else np.log(float(v))**2
 return float(penalty+10*sum((float(v)/2.)**2 for v in (individual_offsets or {}).values()))
