"""Hierarchical sharing: annotated type first, conservative fallback; no free
per-cell fitting by default. Similarity is annotation-based, not proven equality.
Bounds below are modelling priors, not physiological confidence intervals.
"""
import numpy as np
FIELDS={'capacitance_soma':0,'capacitance_axon':1,'leak_soma':2,'leak_axon':3,'E_leak_mV':4,'excitatory_gain':5,'inhibitory_gain':6,'coupling':7,'SK_scale':8,'NaP':9,'axon_bias_pA':10,'gate_speed':11,'source_gain':12,'Na':13,'K':14,'Ca':15,'calcium_tau':16}
MULTIPLIER_BOUNDS=(.5,2.)
FIELD_MULTIPLIER_BOUNDS={"excitatory_gain":(.1,5.),"inhibitory_gain":(.1,5.)} # Effective receptor/release prior, not measured physiology
ABSOLUTE_FIELDS={'calcium_tau_ms':(16,10.,5000.,100.),'gCa_nS':(15,.01,3.,.3)}
ADDITIVE_BOUNDS={'E_leak_mV':(-5.,5.),'axon_bias_pA':(-10.,10.)}

def group_key(row):
 typ=str(row.get('type','')).strip();cl=str(row.get('class','')).strip();nt=str(row.get('predictedNt','')).strip()
 if typ and typ not in {'unknown','Unknown','TBD','SNxxxx'}:
  key=cl+'|type:'+typ
  if row.get('verified_motor_unit_subtype'):key+='|verified_unit:'+str(row['verified_motor_unit_subtype'])
  return key
 return cl+'|hemilineage:'+str(row.get('hemilineage','unknown'))+'|NT:'+nt

def resolve(metadata,group_parameters,individual_offsets=None,class_parameters=None,family_parameters=None,cell_parameters=None):
 """Apply the same parameters to every member of a group. Individual offsets
 retain a legacy additive leak API limited to±2mV. Full per-cell parameter
 overrides are opt-in, namespace-qualified, bounded and explicitly recorded.
 No changes to structural weights, edge direction, receptor sign or stimulus.
 """
 out={};assignments={};available={group_key(row) for row in metadata}
 unknown=set(group_parameters)-available
 if unknown:raise KeyError('Parameter groups absent from this graph: '+', '.join(sorted(unknown)))
 for i,row in enumerate(metadata):
  key=group_key(row);assignments[str(row['bodyId'])]=key
  class_key=str(row.get('class','')).strip().replace('_',' ')
  family_key=class_key+'|NT:'+str(row.get('predictedNt','unknown')).strip().lower()
  values={**(class_parameters or {}).get(class_key,{}),**(family_parameters or {}).get(family_key,{}),**group_parameters.get(key,{})}
  if values:out[i]=values
 identities={str(row.get('connectome_namespace',''))+':'+str(row['bodyId']):i for i,row in enumerate(metadata) if row.get('connectome_namespace')}
 for identity,values in (cell_parameters or {}).items():
  if identity not in identities:raise KeyError('Qualified cell identity absent from this graph: '+identity)
  i=identities[identity];out[i]={**out.get(i,{}),**values}
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
   if name not in FIELDS and name not in ABSOLUTE_FIELDS:raise KeyError(name)
   value=float(value);j=ABSOLUTE_FIELDS[name][0] if name in ABSOLUTE_FIELDS else FIELDS[name]
   if not np.isfinite(value):raise ValueError('Nonfinite group parameter')
   if name in ABSOLUTE_FIELDS:
    _,lo,hi,_=ABSOLUTE_FIELDS[name]
    if not lo<=value<=hi:raise ValueError('Absolute physiological prior exceeded: '+name)
    cell[idx,j]=value
   elif name in ADDITIVE_BOUNDS:
    lo,hi=ADDITIVE_BOUNDS[name]
    if not lo<=value<=hi:raise ValueError('Additive prior exceeded: '+name)
    cell[idx,j]+=value
   else:
    lo,hi=FIELD_MULTIPLIER_BOUNDS.get(name,MULTIPLIER_BOUNDS)
    if not lo<=value<=hi:raise ValueError('Multiplier prior exceeded: '+name)
    cell[idx,j]*=value
 return cell

def regularization(group_parameters,individual_offsets=None):
 """Shrink toward baseline; individual offsets cost more than shared changes."""
 penalty=0.
 for values in group_parameters.values():
  for k,v in values.items():
   if k in ABSOLUTE_FIELDS:penalty+=np.log(float(v)/ABSOLUTE_FIELDS[k][3])**2;continue
   penalty+=(float(v)/5.)**2 if k in ADDITIVE_BOUNDS else np.log(float(v))**2
 return float(penalty+10*sum((float(v)/2.)**2 for v in (individual_offsets or {}).values()))
