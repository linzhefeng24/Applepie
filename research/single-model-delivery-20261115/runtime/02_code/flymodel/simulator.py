"""Public I/O: one model file → neural states → candidate MN pools → native body.
No physiological defaults are hidden here. Generic algebra/index constants are
not a second model. Sense→VNC feedback remains unimplemented and is reported.
"""
from pathlib import Path
import base64,hashlib,io,json,os,platform,xml.etree.ElementTree as ET,zlib
import numpy as np
import yaml
from .dynamics import _kernel

def decode(record):
 raw=base64.b64decode(record['payload'])
 if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Embedded array checksum mismatch')
 with np.load(io.BytesIO(raw),allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}

class Model:
 def __init__(self,path):
  self.path=Path(path).resolve();self.sha256=hashlib.sha256(self.path.read_bytes()).hexdigest()
  with self.path.open() as f:self.config=yaml.load(f,Loader=yaml.CSafeLoader)
  if self.config['schema']!='single_neuromuscular_model_v1':raise ValueError('Unsupported model schema')
  n=self.config['neural'];self.neurons=n['neurons'];self.ids=[x['bodyId'] for x in self.neurons];self.lookup={b:i for i,b in enumerate(self.ids)};self.cells=decode(n['cell_parameters'])['values'];self.edges=decode(n['connectivity']);self.layout=decode(self.config['render']['neural_layout']);self.mapping=self.config['neuromuscular']['mapping'];self.pre=self.edges['pre'];self.post=self.edges['post'];self.count=self.edges['synapse_count'];self.sign=self.edges['transmitter_sign'][self.pre];self.weight=self.count*self.sign
  for spec in n['terminal_efficacy']:
   a=np.array([x['type']==spec['source_type'] for x in self.neurons]);b=np.array([x['type']==spec['target_type'] for x in self.neurons]);sel=a[self.pre]&b[self.post];self.weight[sel]*=spec['gain']
  keep=self.weight!=0;self.pre=self.pre[keep];self.post=self.post[keep];self.weight=self.weight[keep];order=np.lexsort((self.post,self.pre));self.pre=self.pre[order].astype(np.int32);self.post=self.post[order].astype(np.int32);self.weight=self.weight[order];self.offsets=np.r_[0,np.cumsum(np.bincount(self.pre,minlength=len(self.ids)))];self.global_values=np.array([n['global_parameters'][k] for k in n['global_parameter_order']]);self.kinetics=np.array(n['HH_kinetics']['values']);self.aux=np.array(n['solver']['auxiliary_values']);self.last_result=None
 def neuron_ids(self,*,type=None,side=None):
  return [x['bodyId'] for x in self.neurons if (type is None or x['type']==type) and (side is None or x.get('somaSide')==side)]
 def cell_parameters(self,neuron_id):return dict(zip(self.config['neural']['cell_parameter_columns'],self.cells[self.lookup[str(neuron_id)]].tolist()))
 def connections(self,neuron_id,direction='incoming'):
  i=self.lookup[str(neuron_id)];e=self.edges;mask=e['post']==i if direction=='incoming' else e['pre']==i
  return [{'pre':self.ids[int(a)],'post':self.ids[int(b)],'synapse_count':float(w),'predicted_presynaptic_NT':self.neurons[int(a)]['predictedNt']} for a,b,w in zip(e['pre'][mask],e['post'][mask],e['synapse_count'][mask])]
 def run_neural(self,experiment='DN_drive',*,events=None,current_waveform=None,record_ids=None,record_interval_ms=None,ablate_ids=()):
  n=self.config['neural'];protocol=self.config['experiments'][experiment];s=n['solver'];duration=protocol['duration_ms'];sample=s['input_sample_ms'];wave=np.zeros((int(np.ceil(duration/sample))+1,len(self.ids)))
  for e in protocol['events'] if events is None else events:
   ii=[self.lookup[str(b)] for b in e['neuron_ids']];wave[int(e['on_ms']/sample):int(e['off_ms']/sample),ii]=e['current_pA']
  if current_waveform is not None:
   wave=np.asarray(current_waveform,dtype=float)
   if wave.ndim!=2 or wave.shape[1]!=len(self.ids) or len(wave)*sample<duration or not np.isfinite(wave).all():raise ValueError('Current waveform must cover duration and every neuron')
  rec=np.arange(len(self.ids),dtype=np.int64) if record_ids is None else np.array([self.lookup[str(b)] for b in record_ids],dtype=np.int64);abl=np.array([b in set(map(str,ablate_ids)) for b in self.ids]);dt=s['dt_ms'];steps=round(duration/dt);record_interval=s['record_interval_ms'] if record_interval_ms is None else record_interval_ms;stride=max(1,round(record_interval/dt));drive=np.zeros(len(self.ids));out=_kernel(len(self.ids),self.pre,self.post,self.weight,np.zeros(len(self.ids)),drive,abl,dt,steps,0, max(1,round(s['delay_ms']/dt)),self.global_values,self.cells, stride,wave,sample,rec,self.offsets,self.kinetics,self.aux)
  if out[5]:raise FloatingPointError('Neural voltage guard exceeded; result not presented as a valid simulation')
  valid=(steps+stride-1)//stride;r={'spikes':out[0],'voltage':out[1][:valid],'final_soma_mV':out[2],'final_axon_mV':out[3],'final_Ca_uM':out[4],'calcium':out[6][:valid],'currents_pA':out[7][:valid],'conductances_nS':out[8][:valid],'gating_m_h_n':out[9][:valid],'time_ms':np.arange(valid)*stride*dt+dt,'record_indices':rec,'body_ids':np.array(self.ids),'model_sha256':np.array(self.sha256),'experiment':np.array(experiment)};r['run_id']=np.array(hashlib.sha256(self.sha256.encode()+experiment.encode()+wave.tobytes()+abl.tobytes()).hexdigest())
  finals={'voltage':np.stack((out[2][rec],out[3][rec]),axis=1),'calcium':out[4][rec],'gating_m_h_n':out[10][rec],'conductances_nS':out[11][rec],'currents_pA':out[12][rec]}
  if r['time_ms'][-1]<duration:
   for key,value in finals.items():r[key]=np.concatenate((r[key],value[None]),axis=0)
   r['time_ms']=np.r_[r['time_ms'],duration]
  self.last_result=r;return r
 def state(self,neuron_ids,time_ms,*,result=None):
  r=self.last_result if result is None else result
  if r is None:raise RuntimeError('Run the neural model first')
  ii=[self.lookup[str(b)] for b in neuron_ids];rec={int(i):j for j,i in enumerate(r['record_indices'])}
  if any(i not in rec for i in ii):raise KeyError('Requested neuron was not recorded; rerun with it or record_ids=None')
  k=int(np.argmin(np.abs(r['time_ms']-time_ms)));jj=[rec[i] for i in ii];return {'actual_time_ms':float(r['time_ms'][k]),'neuron_ids':list(map(str,neuron_ids)),**{key:r[key][k,jj].copy() for key in ['voltage','calcium','currents_pA','conductances_nS','gating_m_h_n']}}
 def muscle_excitation(self,result=None):
  r=self.last_result if result is None else result;p=self.config['neuromuscular'];bin_ms=self.config['neural']['solver']['spike_bin_ms'];rates=np.zeros((len(r['spikes']),len(self.mapping)))
  for j,m in enumerate(self.mapping):
   if m['MN_indices']:rates[:,j]=r['spikes'][:,m['MN_indices']].mean(axis=1)*self.config['units']['ms_per_s']/bin_ms
  decay=np.exp(-bin_ms/p['filter_tau_ms']);state=np.zeros(len(self.mapping));filtered=np.empty_like(rates)
  for k,row in enumerate(rates):state=decay*state+(1-decay)*row;filtered[k]=state
  return np.clip(filtered/p['rate_scale_Hz'],*p['excitation_bounds'])
 def body(self):return Body(self)
 def simulate_body(self,result=None):
  r=self.last_result if result is None else result;u=self.muscle_excitation(r);body=self.body();p=self.config['demo'];step_ms=body.model.opt.timestep*self.config['units']['ms_per_s'];steps=round(p['body_duration_ms']/step_ms);stride=max(1,round(p['body_record_interval_ms']/step_ms));rows=[]
  for k in range(steps):
   neural_t=p['body_neural_start_ms']+k*step_ms;idx=min(int(neural_t/self.config['neural']['solver']['spike_bin_ms']),len(u)-1);body.step(u[idx])
   if k%stride==0 or k==steps-1:rows.append(body.observe())
  trace={key:np.array([x[key] for x in rows]) for key in rows[0]};trace['neural_time_ms']=p['body_neural_start_ms']+trace['time_s']*self.config['units']['ms_per_s'];trace['model_sha256']=np.array(self.sha256);trace['neural_run_id']=r['run_id'];trace['experiment']=r['experiment'];return body,trace

def _element(rec):
 def value(v):return str(v).lower() if isinstance(v,bool) else ' '.join(map(str,v)) if isinstance(v,list) else str(v)
 x=ET.Element(rec['tag'],{k:value(v) for k,v in rec.get('attributes',{}).items() if v is not None})
 if 'text' in rec:x.text=rec['text']
 for c in rec.get('children',[]):x.append(_element(c))
 return x

class Body:
 def __init__(self,model):
  self.owner=model;cfg=model.config;os.environ.setdefault('MUJOCO_GL',cfg['render']['backends'][platform.system()]);import mujoco
  self.mj=mujoco;assets={}
  for name,rec in cfg['body']['assets'].items():
   raw=zlib.decompress(base64.b64decode(rec['payload']))
   if hashlib.sha256(raw).hexdigest()!=rec['sha256']:raise ValueError('Mesh checksum mismatch')
   assets[name]=raw
  self.model=mujoco.MjModel.from_xml_string(ET.tostring(_element(cfg['body']['mjcf']),encoding='unicode'),assets);self.data=mujoco.MjData(self.model);self.indices=np.array([x['actuator_index'] for x in model.mapping]);self.actadr=self.model.actuator_actadr[self.indices];initial=cfg['body']['initial'];self.data.qpos[:]=initial['qpos'];self.data.qvel[:]=initial['qvel'];self.data.act[:]=initial['activation'];self.data.ctrl[:]=initial['controls'];self.data.time=initial['time_s'];mujoco.mj_forward(self.model,self.data);self.requested=np.zeros(len(self.indices));self.applied=self.requested.copy();self.thorax=self.model.body(cfg['body']['thorax_name']).id
 def step(self,excitation):
  u=np.asarray(excitation,dtype=float)
  if u.shape!=(len(self.indices),) or not np.isfinite(u).all():raise ValueError('Expected one finite excitation per muscle')
  lo,hi=self.owner.config['neuromuscular']['excitation_bounds']
  if np.any(u<lo) or np.any(u>hi):raise ValueError('Muscle excitation outside declared bounds')
  self.requested=u.copy();v=self.data.ctrl.copy();v[self.indices]=u;mask=self.model.actuator_ctrllimited.astype(bool);v[mask]=np.clip(v[mask],self.model.actuator_ctrlrange[mask,0],self.model.actuator_ctrlrange[mask,1]);self.applied=v[self.indices].copy();self.data.ctrl[:]=v;self.mj.mj_step(self.model,self.data)
  if not np.isfinite(self.data.qpos).all():raise FloatingPointError('Body integration failed')
 def observe(self):
  d=self.data;return {'time_s':float(d.time),'qpos':d.qpos.copy(),'qvel':d.qvel.copy(),'all_activation':d.act.copy(),'muscle_activation':d.act[self.actadr].copy(),'muscle_u_requested':self.requested.copy(),'muscle_u_applied':self.applied.copy(),'muscle_force_native':d.actuator_force[self.indices].copy(),'body_up_z':float(d.xmat[self.thorax].reshape(3,3)[2,2]),'extra_applied_force':bool(np.any(d.qfrc_applied) or np.any(d.xfrc_applied))}
 def contacts(self):
  rows=[]
  for k in range(self.data.ncon):
   c=self.data.contact[k];f=np.zeros(6);self.mj.mj_contactForce(self.model,self.data,k,f);rows.append({'geom1':self.model.geom(c.geom1).name,'geom2':self.model.geom(c.geom2).name,'position_native':c.pos.copy(),'force_contact_frame_native':f,'force_on_geom2_world_native':c.frame.reshape(3,3).T@f[:3]})
  return rows
 def restore_for_render(self,trace,index):
  self.data.qpos[:]=trace['qpos'][index];self.data.qvel[:]=trace['qvel'][index];self.data.act[:]=trace['all_activation'][index];self.data.time=trace['time_s'][index];self.mj.mj_forward(self.model,self.data)
