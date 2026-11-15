"""Persist interpretation and provenance of the completed two-cell probe."""
from pathlib import Path
import hashlib,json,platform,subprocess
from importlib.metadata import version
import numpy as np
R=Path(__file__).resolve().parent
report=json.loads((R/'report.json').read_text())
assert set(report['conditions'])=={'baseline','silence_left_INXXX464','silence_right_INXXX464'}
for name,body_id in [('silence_left_INXXX464','929612'),('silence_right_INXXX464','902520')]:
 with np.load(R/(name+'.npz'),allow_pickle=False) as z:
  assert str(z['model_sha256'])==report['model_sha256']
  ids=list(z['body_ids'].astype(str));assert z['spikes'][:,ids.index(body_id)].sum()==0
  for key in z.files:
   if z[key].dtype.kind in 'fc':assert np.isfinite(z[key]).all(),(name,key)
report['conclusions']={'amplitude_asymmetry_observed':True,'anti_phase_alternation_established':False,'unique_or_dominant_pathway_established':False,'single_interneuron_silencing_did_not_abolish_target_output':True,'DN_output_changed_in_interventions':True,'scope':'Existing baseline shows actual muscle activation asymmetry. Whole-neuron perturbations change recurrent activity and do not isolate the direct path or its share. No new body replay was run for the two silencing conditions.'}
(R/'report.json').write_text(json.dumps(report,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prov={'python':platform.python_version(),'versions':{x:version(x) for x in ['numpy','numba','scipy','mujoco','matplotlib']},'code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python research/lateral-pathway-audit-20261115/probe.py','randomness':'no random seed or stochastic input; frozen deterministic input','output_sha256':{p.name:sha(p) for p in sorted(R.glob('*')) if p.is_file() and p.name!='provenance.json'}}
(R/'provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
lines=['# 左右肌肉输出：候选活动链与两次单细胞探查','','## 条件与观察范围','','同一个MaleCNS3988/R2模型、同一个DNg100恒流协议，无优化、无新参数、无外加相位。统计窗400–1450ms。左右按终点后腿命名，源DN可跨侧投射。','', '候选链：','', '- 左后腿：DNg100 10056 → IN17A001 800003 → INXXX464 929612 → MN800621（同池812953）→ LH胫节伸肌。','- 右后腿：DNg100 10045 → IN17A001 800114 → INXXX464 902520 → MN800158（同池809935）→ RH胫节伸肌。','','路径连接存在，各节点有实际活动；这尚不证明主要因果通路或局部CPG源。肌肉对应仍是候选映射。','','## 实际结果','','| 条件 | 左后腿伸肌平均u | 右后腿伸肌平均u | DN实际脉冲与基线一致 |','|---|---:|---:|---|']
for name,c in report['conditions'].items():
 p=c['pairs'][0];lines.append(f"| {name} | {p['left_mean_u']:.4f} | {p['right_mean_u']:.4f} | {c['DN_spike_array_equal_baseline']} |")
a=report['baseline_actual_activation_means'];lines+=['',f"基线真实MuJoCo肌肉平均激活a：左{a['LH:tibia_extensor']:.4f}，右{a['RH:tibia_extensor']:.4f}。该值来自固定躯干、保留地面接触的实际身体回放。",'', '## 结论','','- 当前网络确实驱动左右同名肌肉出现幅度不对称；不是仅动画颜色不同。','- 波包主要仍同时起落；尚未建立左右反相交替，不能把强弱差当作交替步相。','- 两枚INXXX464分别沉默后，下游没有消失，平均输出反而增加；DN实际放电也改变。不能把此链称为唯一、不可替代的主通路，也不能从全细胞干预分离单条边贡献。','- 新干预只重算了神经和u，没有为干预条件重新生成身体视频。原始基线的a是真实身体结果。','- report.json、原始小型npz、活动图、源代码及软件/哈希记录均保留；没有更新交付模型的参数。','', '![基线活动链和幅度差](baseline_paths.png)']
(R/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(report['conclusions'],indent=2))
