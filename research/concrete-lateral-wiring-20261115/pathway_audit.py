"""Specific pathways relevant to left/right alternation; no graph-wide metrics.
Raw EM counts are distinct from predicted transmitter signs and tuned gains.
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
R=Path(__file__).resolve().parent;D=R.parent/'single-model-delivery-20261115';P=D/'build/UnifiedFlyModel'
sys.path.insert(0,str(D/'runtime/02_code'))
from flymodel import Model
m=Model(P/'01_model/model.yaml');e=m.edges
raw={(m.ids[a],m.ids[b]):int(c) for a,b,c in zip(e['pre'],e['post'],e['synapse_count'])}
path=P/'04_results/data/neural_state.npz'
with np.load(path,allow_pickle=False) as z:spikes=z['spikes'].copy()
pairs=[('DN_to_IN17',('10056','800003'),('10045','800114')),('IN17_to_INXXX464',('800003','929612'),('800114','902520')),('INXXX464_feedback_to_IN17',('929612','800003'),('902520','800114')),('INXXX464_to_MN',('929612','800621'),('902520','800158')),('DN_direct_to_MN',('10056','800621'),('10045','800158')),('E_to_cross_inhibitor',('929612','800771'),('902520','801113')),('cross_inhibitor_to_other_E',('800771','902520'),('801113','929612'))]
def edge(a,b):
 x=m.neurons[m.lookup[a]];sel=(m.pre==m.lookup[a])&(m.post==m.lookup[b]);w=float(m.weight[sel].sum())
 return {'pre':a,'pre_type':x['type'],'post':b,'post_type':m.neurons[m.lookup[b]]['type'],'raw_synapse_count':raw.get((a,b),0),'predicted_presynaptic_transmitter':x.get('predictedNt'),'current_model_sign':'excitatory' if w>0 else 'inhibitory_hypothesis' if w<0 else 'absent_or_not_fast_signed','effective_signed_count':w}
report={'scope':'Only the two identified hindleg extensor routes and immediate cross-inhibitory candidates in the extracted MaleCNS3988 model; not a complete-brain symmetry claim.','purpose':'Explain whether concrete excitation/feedback/cross-inhibition can support phase alternation, not merely an amplitude bias.','model_sha256':m.sha256,'baseline_neural_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'side_definition':'left/right names identify the destination hindleg; DNg100 projections in these paths cross sides.','mirrored_edges':[{'role':k,'left_path':edge(*l),'right_path':edge(*r)} for k,l,r in pairs],'bilateral_DN_mutual_excitation':[edge('10045','10056'),edge('10056','10045')],'additional_right_to_left_path':[edge('800114','801356'),edge('801356','800003')],'additional_right_to_left_from_INXXX464':edge('902520','801356'),'observed_interneuron_spike_times_ms':{b:np.flatnonzero(spikes[:,m.lookup[b]]).tolist() for b in ['800771','801113','801356']},'interpretation':['Both selected branches contain excitatory IN17A001-INXXX464 positive feedback with different raw counts.','A two-step cross-inhibitory motif exists through IN07B013 if its glutamatergic outputs are inhibitory as assumed in the current model.','IN07B013 cells actually fire in near-coincident packets, e.g. left218/232ms versus right221/235ms; this does not establish half-cycle alternation.','DN mutual excitation is a candidate synchronizing route, not a demonstrated cause of synchrony.','An additional right-to-left IN14B005 route occurs in the selected local comparison. No mirror is asserted absent from the entire biological connectome.'],'sign_caution':'Raw counts are structural dataset values. ACh excitatory and especially glutamate inhibitory are current receptor/sign assumptions, not per-edge receptor measurements.'}
(R/'report.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# 与左右交替直接相关的具体接线','','目标：周期平均平衡、瞬时交替。只检查两条已定位后腿伸肌链，未统计全图均值或左右总量。','','数字均为原始连接突触计数，不是手调电导；兴奋/抑制是当前模型符号。Glu抑制需受体证据支持。','','| 连接 | 终点左后腿链 | 终点右后腿链 |','|---|---|---|']
for k,l,r in pairs:
 a=edge(*l);b=edge(*r);lines.append(f"| {k} | {l[0]}→{l[1]}：{a['raw_synapse_count']} | {r[0]}→{r[1]}：{b['raw_synapse_count']} |")
lines+=['','## 交叉抑制候选','','```mermaid','flowchart LR',' EL["左 INXXX464 929612"] -->|"115 兴奋"| IL["左 IN07B013 800771"]',' IL -->|"7 模型中抑制"| ER["右 INXXX464 902520"]',' ER -->|"95 兴奋"| IR["右 IN07B013 801113"]',' IR -->|"4 模型中抑制"| EL','```','','两枚IN07B013预测为glutamate，抑制符号为当前模型受体假设。实际记录中左218/232ms、右221/235ms均发放：交叉支路有活动，但未形成半周期交替。','','## 另外两点直接相关的接线','','- 两枚DNg100（10045/10056）相互兴奋，各119个突触。它是共同活动的候选促进结构，未经单独切边验证。','- 右IN17A001 800114→IN14B005 801356（8）→左IN17A001 800003（4，模型中抑制）；选定细胞的这次两步检查未找到反向镜像支路。这不等于完整生物连接组没有更长或未提取的对应路径。','','结论：两侧局部框架相似，但突触计数和部分具体路由不镜像。已有可研究的交叉抑制结构；当前实际活动仍接近同步，不能把结构存在当作交替已发生。']
(R/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'mirrored_edge_roles':len(pairs),'output':str(R/'report.json')},indent=2))
