"""Review downloaded1000-update outputs; this is not a new neural rerun."""
from pathlib import Path
import argparse,hashlib,io,json,zipfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--validation',type=Path,required=True);p.add_argument('--checkpoint',type=Path,required=True);a=p.parse_args()
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
assert sha(a.validation)=='569e64258dac14739684725603af5c5565b762bc04b29f03d6b2985a3415b4bf'
assert sha(a.checkpoint)=='44304aa747c7078755cb16720d39a32ec839cc5e4953b47fcb3bf2fbd888fe70'
with zipfile.ZipFile(a.checkpoint) as z:
 assert z.testzip() is None
 with np.load(io.BytesIO(z.read('latest-optimizer.npz')),allow_pickle=False) as s:
  updates=int(s['completed_updates']);best_step=int(s['best_step'])
 history=json.loads(z.read('history.json'));assert updates==1000 and {x['parameters_after_updates'] for x in history}==set(range(1001))
with zipfile.ZipFile(a.validation) as z:
 assert z.testzip() is None
 result=json.loads(z.read('report.json'));base=result['baseline_full_network'];new=result['conditions']['DN_drive']
 with np.load(io.BytesIO(z.read('muscle-u.npz')),allow_pickle=False) as s:
  u=s['u'];target=s['target_u'];ids=list(s['muscle_ids']);mapped=s['mapped']
 with np.load(io.BytesIO(z.read('DN_drive.npz')),allow_pickle=False) as s:
  cells=list(s['body_ids'].astype(str));times={b:np.flatnonzero(s['spikes'][:,cells.index(b)]).tolist() for b in ['929612','902520','800771','801113','800621','800158']}
 metrics={k:{'baseline':base[k],'candidate':new[k],'relative_reduction_percent':100*(base[k]-new[k])/base[k]} for k in ['train_mse_mapped','holdout_mse_mapped','holdout_mse_all130']}
 pairs=[];window=(np.arange(len(u))>=400)&(np.arange(len(u))<1400)
 for name in ['tibia_extensor','pleural_remotor_and_abductor']:
  l=ids.index('LH:'+name);r=ids.index('RH:'+name)
  pairs.append({'left_muscle':ids[l],'right_muscle':ids[r],'window_ms':[400,1400],'left_mean_u':float(u[window,l].mean()),'right_mean_u':float(u[window,r].mean()),'zero_lag_correlation':float(np.corrcoef(u[window,l],u[window,r])[0,1]),'interpretation':'Descriptive selected-pair activity; not proof of stable opposite-phase coordination.'})
 fig,ax=plt.subplots(2,1,figsize=(11,6),sharex=True,layout='constrained')
 for side in ['LH','RH']:
  col=ids.index(side+':tibia_extensor');ax[0].plot(np.arange(len(u)),u[:,col],label=side+' candidate u');ax[1].plot(np.arange(len(u)),target[:,col],label=side+' target u')
 for x in ax:x.set_xlim(200,1400);x.set_ylim(-.03,1.03);x.legend();x.grid(alpha=.2)
 ax[0].set_ylabel('Full-network candidate');ax[1].set_ylabel('Fixed globally stretched target');ax[1].set_xlabel('Neural time (ms)');fig.suptitle('1000 updates, selected checkpoint123: waveform improvement is not established alternation')
 fig.savefig(R/'homologous-muscle-u.png',dpi=140);plt.close(fig)
fg=result['conditions']['BPN_FG']['rates_500_950_Hz'];steer=result['conditions']['PFL3_left']['rates_500_950_Hz'];brk=result['conditions']['BRK']['rates_500_950_Hz']
summary={'scope':'Freshly downloaded and SHA-verified GitHub artifacts; analysis only, not a new simulation or training run.','completed_updates':updates,'best_training_step':best_step,'history_update_indices':len(history),'upstream_training_source_revision':'da9d0e17d1215879c894b9668dbc00cd77f03163','input_sha256':{'full_validation_zip':sha(a.validation),'optimizer_checkpoint_zip':sha(a.checkpoint)},'audit_script_sha256':sha(Path(__file__)),'full_network_validation_status':result['status'],'mapped_channels':int(mapped.sum()),'unmapped_channels':int((~mapped).sum()),'metrics':metrics,'max_relative_parameter_change':result['max_relative_change'],'rms_relative_parameter_change':result['rms_relative_change'],'affected_cells':result['cell_parameters_changed'],'quiet_spikes':result['conditions']['quiet']['spikes'],'PFL3_DNa02_Hz':{b:steer[b] for b in ['523769','10360']},'BRK_BON1_candidate_Hz':{b:brk[b] for b in ['39880','800041']},'FG_window_DNg100_Hz':{b:fg[b] for b in ['10045','10056']},'FG_baseline_reference_Hz':{'10045':2.2222222222222223,'10056':2.2222222222222223},'FG_comparison_scope':'Same saved R2 BPN+FG protocol; residual firing increases after fit. This is not a matched BPN-alone causal assay or proof of behavioural stopping.','selected_homologous_pairs':pairs,'selected_spike_times_ms':times,'left_right_alternation_established':False,'full_laboratory_phenomena_reproduction_claimed':False,'adoption':'Keep as fitted candidate; waveform fit improves but phase coordination and all neural constraints have not passed.'}
(R/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
text=f'''# 1000轮完成后的结果核对

真实完成{updates}次Adam参数更新，历史记录包含0至1000共1001个更新编号。最佳训练检查点为第{best_step}轮，后续更新没有提前停止。训练是260细胞的局部边界回放代理梯度BPTT，验证是原始3988细胞硬脉冲网络自由运行，两者不混称。

## 原始完整网络中的u拟合

| 项目 | 基线 | 候选 | MSE下降 |
|---|---:|---:|---:|
'''
for key,label in [('train_mse_mapped','训练时段104映射通道'),('holdout_mse_mapped','留出时段104映射通道'),('holdout_mse_all130','留出时段全部130通道，含26缺口')]:
 x=metrics[key];text+=f"| {label} | {x['baseline']:.6f} | {x['candidate']:.6f} | {x['relative_reduction_percent']:.2f}% |\n"
text+=f'''
参数最大相对变化{result['max_relative_change']*100:.2f}%，共享变量的RMS变化{result['rms_relative_change']*100:.2f}%，低于±20%限制。207个类型共享变量影响{result['cell_parameters_changed']}枚细胞。没有更改解剖连接计数、递质符号、肌肉模型或读出映射。26个映射缺口没有被填补。

## 具体通路核对

- 无刺激全网0次放电。
- 左功能输出侧PFL3刺激时，DNa02左523769为{steer['523769']:.2f}Hz、右10360为{steer['10360']:.2f}Hz，同侧优势保留；不等于完整转向实验通过。
- BRK刺激时BON1候选39880/800041仍响应，分别{brk['39880']:.2f}/{brk['800041']:.2f}Hz；不是实验GCaMP波形的定量复现。
- BPN+FG协议中DNg100的FG时窗残余为{fg['10045']:.2f}/{fg['10056']:.2f}Hz，原R2同条件为2.22/2.22Hz，抑制变弱；不能把所有原有现象都记成改善。
- 后腿同名伸肌及IN07B013两侧记录仍有大量同时起落，例如IN07B013左218/233ms、右222/235ms。未建立稳定左右反相交替，不能把均值强弱差作为目标已达成。

这是对已上传原始结果的核验，不是重新训练或重新应用旧修改。候选未自动替换基线，也未发布新的Release。下载来源及SHA、逐细胞数据见summary.json和已保存的训练Release清单。

![左右同名肌肉实际波形](homologous-muscle-u.png)
'''
(R/'README.md').write_text(text)
print(json.dumps({k:summary[k] for k in ['completed_updates','best_training_step','metrics','max_relative_parameter_change','left_right_alternation_established']},indent=2))
