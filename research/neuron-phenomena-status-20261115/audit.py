"""Cell/path-specific status audit of the delivered frozen R2 model.
Reads existing runs only; no tuning, new simulation, or transferred pass labels.
"""
from pathlib import Path
import hashlib,json,sys,subprocess
import numpy as np
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
D=ROOT/'research/single-model-delivery-20261115';T=ROOT/'research/brake-retuning-20261115/results'
sys.path.insert(0,str(D/'runtime/02_code'))
from flymodel import Model
m=Model(D/'build/UnifiedFlyModel/01_model/model.yaml')
used={}
def read(p):
 used[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 return json.loads(p.read_text())
def diag(tag,case):return read(T/tag/(case+'-diagnosis.json'))
def cell(d,b,w='500_950'):return next(c for c in d['cells'] if c['body_id']==b)['windows'][w]
def rates(d,ids,w='500_950'):return {b:cell(d,b,w)['rate_Hz'] for b in ids}
B=diag('terminal-r2','BRK');C=diag('terminal-r2','control');P=diag('validation-r2','PFL3L');F=diag('validation-r2','BPN+FG')
# Counts of newly inspected cells are read directly from the existing full spike arrays.
def spike_rates(case,ids):
 p=T/'terminal-r2'/(case+'.npz');used[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 with np.load(p,allow_pickle=False) as z:return {b:float(z['spikes'][500:950,m.lookup[b]].sum()/0.45) for b in ids}
rows=[]
def add(id,structure,expected,status,observed,ids=(),limits='',sources=()):
 rows.append(dict(id=id,structure=structure,expected=expected,status=status,observed=observed,namespace='MaleCNS_v1.0 unless explicitly literature-only',cell_ids=list(ids),limits=limits,literature_sources=list(sources)))
add('PFL3_DNa02_direction','左功能输出侧PFL3群→DNa02_L/R','同侧DNa02响应较强','qualitative_response_supported',rates(P,['523769','10360']),['523769','10360'],'500–950ms；51.11 vs 6.67Hz。只验证左右响应差，不验证转向、对侧抑制或中继必要性。',['10.1016/j.cell.2024.08.033'])
add('PFL3_DNa03_LAL010','左功能输出侧PFL3群→DNa03/LAL010','同侧兴奋中继被募集','qualitative_response_supported',rates(P,['519624','10975','14986','519129']),['519624','10975','14986','519129'],'同窗DNa03 L/R=22.22/6.67Hz，LAL010 L/R=57.78/0Hz；未逐边阻断，不能指定哪支路造成DNa02响应。',['10.1016/j.cell.2024.08.033'])
add('DNa02_push_pull','DNa02_L↔网络↔DNa02_R','一侧兴奋且另一侧相对匹配基线受抑制','not_tested',rates(P,['523769','10360']),['523769','10360'],'未做平衡基线、配对条件或对侧抑制支路阻断；左右差不能替代push-pull，也不代表直接互抑。')
bon=['39880','800041']
add('BRK_BON1','BRK候选AN19A018→BON1候选IN27X001','BRK刺激提高BON1活动','qualitative_response_supported',{'BRK_Hz':rates(B,bon),'control_Hz':rates(C,bon),'BRK_Ca_uM':{b:cell(B,b)['Ca_uM'] for b in bon}},bon,'MaleCNS IN27X001经mancBodyid10441/10348关联2024文献BON1；文献旧类型IN27X003，不按名称强行合并。模型Ca不是GCaMP ΔF/F；未复现2秒刺激/6Hz采样的定量波形。',['10.1038/s41586-024-07854-7'])
relay=['800051','800053']
add('BRK_IN07B001','BRK候选AN19A018→IN07B001_L/R','手调后保持晚期中继活动','model_mechanism_only',rates(B,relay,'1000_1450'),relay,'17.78/24.44Hz；这是调参检查，不是独立实验现象。IN07B001不是BON1。末端共享效力×3.5未经实测。')
lbl=m.neuron_ids(type='LBL40')
add('MDN_LBL40','MDN四细胞→LBL40_L/R','MDN募集后退运动前中继','qualitative_response_supported',{'MDN_Hz':spike_rates('MDN',lbl),'control_Hz':spike_rates('control',lbl)},lbl,'R42.22/L48.89Hz；只证明模型放电方向一致，未核对LBL40钙波形、LUM9输出和沉默后的支撑功能。',['10.1038/s41467-020-19936-x'])
add('FG_BPN','FG候选GNG458→BPN下游→DNg100','FG减弱前行指令','partial',{w:rates(F,['10045','10056'],w) for w in ['200_450','500_950','1000_1450']},['26344','520884','10045','10056'],'刺激前32/32Hz、FG窗2.22/2.22Hz、之后20/20Hz；仍有残余，且不同时间窗比较，缺少R2 BPN单独的同时窗对照。未证明行为停止。',['10.1038/s41586-024-07854-7'])
ra=read(ROOT/'research/rhythm-pathway-audit-20261115/report.json')
add('DN_MN_muscle','DNg100→MN801946/803314/801234→候选肌肉','神经重复波包驱动肌肉u','model_output_observed',ra['examples'],['10045','10056','801946','803314','801234'],'有直接兴奋边和实际MN/u记录；肌肉对应为候选映射。未通过切边证明这些直连的因果必要性，也未定位局部CPG。')
add('CPG_origin','DNg100→E1/E2/I1/I2→MN','局部回路生成并传递节律','not_tested','当前观察到DN自身重复放电簇，可经直达MN通路传递；不能据此确认局部CPG。',limits='旧MANC E1=10707,E2=11751,I1=13905,I2=10242，不把这些ID移植到MaleCNS。')
add('alternating_output','上述MN池及左右/拮抗肌群','腿间和拮抗肌形成所需相位差','not_achieved_in_inspected_examples','已检查的RM/RF/LM示例激活近同步，u多次饱和到1。',ids=['801946','803314','801234'],limits='不能由这三个肌肉外推所有130路；全六腿的正确协调尚未建立。')
items=[
('CPG_ablation','E1/E2/I1/I2小回路','E1/E2沉默取消节律；I1/I2单消融可保留','not_tested','最终MaleCNS模型没有对应完整消融验证；旧MANC局部结果单列。'),
('DN_frequency','DNg100→节律回路','增强刺激使输出频率随之增加','not_tested','当前仅160pA协议；旧MANC模型曾非单调。'),
('DNb08_motif','DNb08→E1/E2/E4/E5/I2','五细胞基序、负载依赖及选择性MN募集','not_tested','DNb08标签有12044/12075/12189/12550；不能把全部同名细胞都当作论文驱动系精确覆盖。'),
('PFL2_gain','PFL2→双侧DNa03/LAL010→DNa02','对称输入只改变转向增益','not_tested','缺少最终R2左右平衡及组合刺激的同条件测试。'),
('DNa02_phase','DNa02523769/10360→前运动网络','步相锁定及同侧三腿步幅缩短','not_tested','当前神经活动差不是步相锁定或三腿运动学证据。'),
('DNg13_gate','DNg13_11074/512006→前运动网络→MN','支撑相促后向、摆动相促前向；不同于DNa02','not_implemented','未建立接触/步相依赖的感觉门控闭环。'),
('LBL40_motor','MDN→LBL40_801214/801246→LUM9','胫节屈曲、支撑发力及消融效应','partial','已观察上游LBL40募集；LUM9精确运动单位身份及其肌肉功能因果未确认。'),
('LUL130','MDN→LUL130','抬后腿、启动摆动及消融效应','identity_unresolved','当前图没有LUL130精确标签；不能用同家族细胞代替并宣布完成。'),
('MF14','MDN→MF14_T1/T2/T3','T1/T2净兴奋、T3净抑制','identity_unresolved','MF14逐节段对应尚未确认；没有最终版同条件响应测试。'),
('LBL40_LUL130_mutual','LBL40↔LUL130','相互抑制','hypothesis_not_acceptance_test','原资料为机制假说，不作为已确认的必须满足连接。'),
('BRK_stance','BRK→VNC→MN','摆动结束落地再锁定；支撑相立即制动','not_implemented','固定根关节不等于BRK制动；最终身体没有感觉回接VNC。'),
('BRK_angle','BRK→辅屈肌/伸肌MN','屈伸姿态不同，募集的肌群组合不同','not_implemented','没有关节角度到该回路的已识别反馈和反射门控。'),
('BRK_MDN','MDN+BRK→后退运动通路','BRK阻断MDN后退','not_verified','有同参数神经联合刺激记录，但无相应自由/去头行为或支撑锁定验证；不以LBL40必须沉默作替代判据。'),
('FG_BB_direction','FG/BB/BRK分别与MDN、P9组合','方向选择性停止和原地转向','not_tested','最终版未做完整组合及对应身体测量；FG/BB对MDN不阻断与BRK制动需分开检验。'),
('BPN_P9','BPN与P9/DNp09','单侧BPN直行、单侧P9同侧转、共刺激组合输出','not_tested','最终版缺少单侧和组合行为验证；P9群体募集未逐个做因果检查。'),
('DNg74_hook','DNg74_a/b⊣chief9A⊣hook；claw保留','动作相关突触前感觉抑制/去抑制','not_implemented','DNg74_a/b存在，但chief9A/hook/claw精确身份及终末门控未落实；静态负权重不是终末抑制机制。'),
('FeCO_encoder','claw/hook/club→局部VNC','位置滞回、方向性运动、振动选择性','not_implemented','未将真实关节位置/速度/振动转成已识别感觉神经元输入。'),
('13Ba_9Aa_10Ba','FeCO→13Bα/9Aα/10Bα','角度阈值、振动/位置融合与刺激冻结','not_implemented','存在广义10B/13B细胞不等于确认这些记录细胞亚型；缺少对应感觉输入和行为测试。'),
('club_9Ba','左右club→9Ba','双侧振动输入汇合及MLA阻断','not_implemented','没有精确亚型/刺激/药理协议。'),
('club_10Ba','T1L club→T1L/T2R 10Ba','跨节段响应和局部残余的药理差异','not_implemented','无六腿club输入映射或对应受体阻断模型。'),
('claw_hook_13Bb','伸展claw/hook→13Bb','伸展相位响应及大角度紧张响应','not_implemented','没有该感觉转导及明确13Bb细胞身份。'),
('CxHP8','club→CxHP8→运动输出','前极限检测、后向运动与反射反转','identity_unresolved','没有CxHP8精确对应，也没有位置依赖感觉反馈。'),
('MN_classes','慢/中/快胫节屈肌MN','30Hz慢型静息、募集顺序及150/300/700MΩ','partial','旧单细胞参考模板有支持；最终EM运动单位未逐一映射快/中/慢，不能宣布全池实测匹配。'),
('MN_reflex','感觉输入→慢/中/快MN','运动状态下反射反转、慢单位选择性撤募','not_implemented','没有感觉和状态依赖反射回路。'),
('MN_Rdl','前运动GABA→MN_Rdl','Rdl干预改变步长/步频及摆动支撑时长','not_tested','存在模型GABA电导不等于Rdl亚基表达/敲低及步态结果已复现。'),
('19A_19B','19B/19A及跨腿耦合','T2选择性运动、前腿左右耦合','not_tested','未做最终版谱系刺激/消融；19B→19A符号仍需逐边身份核对。'),
('specific_lineages','1A、13B、21A、23B各自少数细胞/群体','各自的前进、姿态、屈曲、跨节段运动表型','not_tested','未精确映射每个实验驱动系覆盖，不能把整个谱系当一个已验证神经元。'),
('FG_hunger','糖GRN→FG','饥饿增强FG钙响应','not_implemented','无饥饿、糖感觉状态或实验钙观测模型。'),
('load_CS','campaniform sensilla→VNC→MN','受力反馈、支撑行程与协调改变','not_implemented','身体有接触力，不等于它已传入感觉细胞。'),
('AN_HS','LAL-PS-ANcontra→间接脑网络→HS','速度编码、步相电位反馈、主动/被动相位差','identity_unresolved','最终图/记录中未确认该对细胞及HS反馈链；无感觉闭环，不能把相关性当直接AN→HS连接。'),
('5HT','VNC 5-HT群体→运动网络','行走起始相关活动、广义激活减速','not_implemented','当前快突触图没有完整单胺慢调制动力学。'),
('other_DNs','DNg75/97/55/16与DNg100小群组合','步频、协调、步幅的不同组合效应','not_tested','旧MANC仅有神经代理；最终MaleCNS版本未做同条件组合行为验证。')]
items += [
('DNa01_DNb05_06','DNa01、DNb05、DNb06','左右钙活动差与角速度相关','not_tested','未进行对应运动行为/钙信号记录协议；不能把神经率直接当ΔF/F。'),
('DNa03_silence','DNa03_L/R','单侧沉默产生对侧角速度偏置','not_tested','上游刺激时DNa03活动升高不等于该消融行为已完成。'),
('EPG_PFL3','EPG/Δ7→PFL3→DNa02','航向余弦活动包、±67.5度偏移及方向误差正弦输出','not_implemented','没有带真实航向/目标输入的已验证中央复合体导航计算。'),
('MAN_state','MAN/dMAN→VNC','前行抑制、后退维持及六腿pushdown相关活动','not_tested','未对最终模型进行准确驱动系/行为状态匹配验证。'),
('DNg11_12','DNg11与特定DNg12亚型→9A等','前腿理毛命令及亚型特异输入','not_tested','没有精确亚型和理毛任务验证，不与行走命令混为一谈。'),
('DopaMeander','DopaMeander→运动回路','前行/同侧转向和飞行状态门控','not_implemented','未建立多巴胺慢调制和飞行状态门控。'),
('groom_13A_13B','13A/13B理毛抑制回路','沉默降低振荡频率并改变前腿间距，持续激活增加频率变异','not_tested','这些是理毛条件现象，最终模型未执行该任务；不作为无条件行走指标。'),
('DNp09_population','DNp09/P9→下游DN群体','群体前馈/递归招募以及去头、追偶条件差异','not_tested','BPN+FG或PFL3的响应记录不能替代P9群体及行为条件的实验。')]
for id,st,ex,status,reason in items:add(id,st,ex,status,None,limits=reason)
old=read(ROOT/'research/conductance-rebuild-20261114/results/phenomena-audit.json')
legacy=[x for x in old['tests'] if x['id'] in ['E1_necessity','E2_necessity','I2_connected_rhythm','I1_I2_single_ablation_redundancy','intact_stimulus_frequency_monotonic','adult_recruitment_order','adult_Rin_and_rest','DNb08_MN_periodicity']]
inv=read(ROOT/'research/conductance-rebuild-20261114/data/phenomena-inventory.json')
report={'scope':'Delivered single MaleCNS3988 R2 model; audit of existing traces, no new simulation or tuning','model_sha256':m.sha256,'stimulus_protocols':m.config['experiments'],'PFL3_side_definition':'PFL3L/R groups use functional_output_side from pulse_neural_panel.py, not somaSide; source group IDs are preserved in the protocols.','audit_source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'fully_reproduced_laboratory_experiments':[],'interpretation':'qualitative_response_supported is a scoped neural response, not a complete experimental reproduction, causal pathway validation or calibrated calcium fit. Entries overlap; not a success percentage.','checks':rows,'legacy_MANC_only':{'namespace':'MANC; different graph/parameters, not passes of the delivered model','core_ids':{'DNg100':10093,'E1':10707,'E2':11751,'I1':13905,'I2':10242},'tests':legacy},'literature_claims_retained_without_inheriting_passes':inv['claims'],'input_sha256':used}
(R/'status.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
lines=['# 逐神经元/小通路状态审计','',report['scope'],'','模型SHA-256: '+m.sha256,'','“定性响应支持”仅限所列神经读数；没有完整实验现象被全部复现。BRK后IN07B001持续放电是模型检查，不是实验真值。','', '| ID | 神经元/通路 | 目标现象 | 状态 | 证据与边界 |','|---|---|---|---|---|']
for x in rows:lines.append('| '+ ' | '.join(str(x[k]).replace('|','/') for k in ['id','structure','expected','status','limits'])+' |')
lines+=['','## 旧MANC版本（不计入当前版本通过）','']
for x in legacy:lines.append('- '+x['id']+': '+x['status']+'；'+x['scope'])
lines+=['','完整数值、细胞ID、146条原始文献记录和输入SHA见status.json。审计程序只读取已有文件。']
(R/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'checks':len(rows),'literature_claims':len(inv['claims']),'fully_reproduced_laboratory_experiments':0,'output':str(R/'status.json')},ensure_ascii=False))
