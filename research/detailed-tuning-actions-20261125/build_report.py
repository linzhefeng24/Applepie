"""Read-only action-level audit; no simulation, fitting, or model changes.

python build_report.py --package /path/to/flybody_male_full --r2 /path/to/Manual_FreeBody/01_model/model.yaml
"""
from pathlib import Path
import argparse,base64,collections,csv,hashlib,io,json,os,re,subprocess,sys
import numpy as np
import yaml
from action_catalog import A

R=Path(__file__).resolve().parent
ROOT=R.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(spec):
    b=base64.b64decode(spec['payload'])
    assert hashlib.sha256(b).hexdigest()==spec['sha256']
    with np.load(io.BytesIO(b),allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def val(v):
    if isinstance(v,(list,dict)):return json.dumps(v,ensure_ascii=False)
    return str(v)
def cell(v):return val(v).replace('|','／').replace('\n','<br>')
def tab(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(cell(x) for x in row)+' |' for row in rows])+'\n\n'
def fmt(v):return f'{float(v):.12g}'
def writecsv(name,rows):
    if not rows:return
    with (R/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def add_pdf_outline(path):
    """Add explicit bookmarks when the local Chromium omits its HTML outline."""
    import fitz
    doc=fitz.open(path);toc=[]
    for pi,page in enumerate(doc):
        for block in page.get_text('dict')['blocks']:
            if 'lines' not in block:continue
            spans=[s for line in block['lines'] for s in line['spans']]
            if not spans:continue
            title=''.join(s['text'] for s in spans).strip();size=max(s['size'] for s in spans)
            if pi and size>=16:toc.append([1,title,pi+1])
            elif size>=11 and re.match(r'^[NMH]\d{2}\s',title):toc.append([2,title,pi+1])
            elif size>=11 and re.match(r'^(LF|RF|LM|RM|LH|RH)腿$',title):toc.append([2,title,pi+1])
            elif size>=10 and re.match(r'^(LF|RF|LM|RM|LH|RH):',title):toc.append([3,title,pi+1])
    # Prevent a jump >1 when a very long heading is split into separate blocks.
    last=0
    for row in toc:row[0]=min(row[0],last+1);last=row[0]
    doc.set_toc(toc);tmp=path.with_suffix('.bookmarked.pdf');doc.save(tmp,garbage=3,deflate=True);doc.close();tmp.replace(path)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--r2',type=Path,required=True);args=ap.parse_args()
    mp=args.package/'01_model/model.yaml';model=yaml.load(mp.read_text(),Loader=yaml.CSafeLoader)
    old=yaml.load(args.r2.read_text(),Loader=yaml.CSafeLoader)
    neurons=model['neural']['neurons'];oldn=old['neural']['neurons'];c=decode(model['neural']['cell_parameters'])['values'];oc=decode(old['neural']['cell_parameters'])['values'];cols=model['neural']['cell_parameter_columns']
    assert cols==old['neural']['cell_parameter_columns']
    oi={str(x['bodyId']):i for i,x in enumerate(oldn)};ni={str(x['bodyId']):i for i,x in enumerate(neurons)}
    mapping=model['neuromuscular']['mapping'];oldmap={x['muscle_id']:x for x in old['neuromuscular']['mapping']}
    ph=json.loads((args.package/'03_phenomena/phenomena.json').read_text())
    historical74=ph['key_checks_full_model']['pathway_excitability_tune']
    targeted24=set(historical74['muscles']);recorded74=set(historical74['mn_body_ids'])
    assert len(targeted24)==24 and len(recorded74)==74
    mn_to_muscles=collections.defaultdict(list)
    for m in mapping:
        for i in m['MN_indices']:mn_to_muscles[i].append(m['muscle_id'])
    # Explicit package source indices are resolved against THIS immutable model.
    dep=[3607,3539,3559,3961,3966,3975];lev=[3532,3565,3572,3416]
    depids={str(neurons[i]['bodyId']) for i in dep};levids={str(neurons[i]['bodyId']) for i in lev}
    prelr=c.copy()
    for i in dep:prelr[i,5]/=.65;prelr[i,2]/=1.3;prelr[i,9]/=.7;prelr[i,10]+=.25
    for i in lev:prelr[i,5]/=1.35;prelr[i,2]/=.9
    # 74 is a reconstructed signature, not a recovered historical selected-ID log.
    inferred74={i for i in range(len(c)) if neurons[i].get('superclass')=='vnc_motor' and np.isclose(prelr[i,5],18) and np.isclose(prelr[i,2],1.652272949657866*.8)}
    assert len(inferred74)==74
    assert {str(neurons[i]['bodyId']) for i in inferred74}==recorded74
    changes=[];byid={}
    for j,n in enumerate(neurons):
        bid=str(n['bodyId'])
        if bid not in oi:continue
        k=oi[bid];diff=np.flatnonzero(c[j]!=oc[k]);local=[]
        for z in diff:
            row={'MaleCNS_ID':bid,'type':n.get('type'),'superclass':n.get('superclass'),'parameter':cols[z],
                'R2_value':float(oc[k,z]),'full_model_value':float(c[j,z]),'direction':'↑' if c[j,z]>oc[k,z] else '↓',
                'ratio_if_defined':float(c[j,z]/oc[k,z]) if oc[k,z] else '基线零，不能作比例',
                'provenance':'本次逐数组快照比较；不是恢复的逐次调节日志'}
            changes.append(row);local.append(row)
        if local:byid[bid]=local
    writecsv('all_retained_cell_parameter_deltas.csv',changes)
    currentids=set(byid);changed_nonmn={ni[b] for b in byid if neurons[ni[b]].get('superclass')!='vnc_motor'}
    changed_mn={ni[b] for b in byid if neurons[ni[b]].get('superclass')=='vnc_motor'}
    # Anatomical direct input lookup: static relation, NOT functional causality.
    edges=decode(model['neural']['connectivity']);mask=np.isin(edges['pre'],list(changed_nonmn)) & (edges['synapse_count']>0)
    incoming=collections.defaultdict(set)
    for pre,post in zip(edges['pre'][mask],edges['post'][mask]):incoming[int(post)].add(int(pre))
    external=set(model['neuromuscular']['external_drive']['muscle_ids'])
    # Additional snapshot changes were omitted by the earlier, too-general report.
    pfl=[str(n['bodyId']) for n in neurons if str(n['bodyId']) in byid and n.get('type') in {'PFL2','PFL3'}]
    other=[str(neurons[i]['bodyId']) for i in sorted(changed_nonmn) if neurons[i].get('type') not in {'PFL2','PFL3'}]
    snapshot_summary={'R2_sha256':digest(args.r2),'current_sha256':digest(mp),'shared_cells':len(set(oi)&set(ni)),
        'changed_cells':len(byid),'changed_MN':len(changed_mn),'changed_non_MN':len(changed_nonmn),
        'PFL_changed_ids':pfl,'other_non_MN_changed_ids':other,'inferred_74_MN_ids':[str(neurons[i]['bodyId']) for i in sorted(inferred74)],
        'explicit_depressor_MN_ids':sorted(depids),'explicit_levator_MN_ids':sorted(levids),
        'recorded_74_MN_ids':sorted(recorded74),'recorded_24_muscles':sorted(targeted24),
        'signature_matches_recorded_74':True,
        'warning':'Snapshot differences do not identify tuning intention/order; the package records 24 muscles and 74 IDs; the independent signature confirms those IDs, not every historical screening step.'}
    (R/'snapshot_comparison.json').write_text(json.dumps(snapshot_summary,ensure_ascii=False,indent=2)+'\n')
    # Source ledger includes both narrative and executable sources.
    sources={}
    for pattern in ['research/conductance-rebuild-20261114/configs/manual-*.json','research/conductance-rebuild-20261114/results/manual-mechanism/*diagnosis.json']:
        for p in ROOT.glob(pattern):sources[str(p.relative_to(ROOT))]={'sha256':digest(p),'bytes':p.stat().st_size}
    for p in [ROOT/'research/conductance-rebuild-20261114/asymmetry_refinement.py',ROOT/'research/conductance-rebuild-20261114/asymmetry_guard_refine.py',ROOT/'research/conductance-rebuild-20261114/trace_manual_network.py',ROOT/'research/conductance-rebuild-20261114/grouped_parameters.py',ROOT/'research/conductance-rebuild-20261114/ASYMMETRY.md',ROOT/'research/conductance-rebuild-20261114/MANUAL_RESULTS_20261115.md',ROOT/'research/body-sensory-20261115/RESULTS.md',ROOT/'research/manual-extension-review-20261119/selected_trial.json',ROOT/'research/core-bypass-localization-20261119/candidate_decision.json',ROOT/'research/brake-retuning-20261115/configs/brake-terminal-r2.json']:
        sources[str(p.relative_to(ROOT))]={'sha256':digest(p),'bytes':p.stat().st_size}
    (R/'actions.json').write_text(json.dumps({'scope':'Historical action records with current equation explanations; not new experiments','actions':A},ensure_ascii=False,indent=2)+'\n')
    tx='''---
title: "手动调参逐项决策表：现象、细胞层级与特定肌肉"
author: "Applepie · 以可核对操作记录为准"
date: "2026年11月25日·修订版"
lang: zh-CN
---

# 本版直接回答的问题

您要的是每个现象/肌肉究竟怎么调：看到什么→沿通路定位到哪里→改DN、VNC、MN还是输出接口→改哪个参数→旧值、新值及方向→为什么选择它→试后怎样→为什么保留/撤回。本版以这些**操作决策表**为主体，不再用大量现象观察和最终值表代替调节过程。

VNC是解剖区域，MN也位于VNC；为避免歧义，本文“VNC层”专指VNC中间神经元，“MN层”单独列出。还分别列脑内细胞、DN、感觉输入、神经肌肉接口、肌肉控制u(t)、肌肉/身体力学。

**结论先列清：**后来AB募集调整主要改74个MN的兴奋受体/胞体漏电；跗节对齐又改指定10个MN。早期肌肉相关诊断确实也试过VNC抑制源、DN→MN末端、MN门控与输出增益。实验现象调整则有脑内、DN、VNC、受体、Ca和突触时间常数等层级。不能概括为“全程只有MN”或“每块肌肉都联合优化过上游”。

本次没有训练或仿真。明确证据分三类：**记录明确**（脚本/参数/历史结果可对照）；**快照比较**（本次对原R2与最终模型逐值比较）；**方向解释**（按实际方程解释某一改动预期影响，不冒称当时已有完整书面推理）。没有记录的旧值、顺序和否决理由会留空，不能补造。

另纠正上一版：部分早期流程并非“无优化器”。神经候选由命名试验给定，但肌肉固定增益用minimize_scalar求解，部分候选由训练分数自动选择。它们与后来的逐通路手动诊断分别列出，不把自动标定包装成纯手调。

# 按层级核对：不同肌肉相关阶段到底动了哪里

'''
    tx+=tab(['阶段','DN/脑内','VNC中间神经元','MN','输出接口/肌肉/身体'],[
        ['H01早期屈伸粗拟合','继承基线','继承基线','兴奋、SK、gate_speed命名候选','逐通道固定gain数值求解；滤波候选'],
        ['H04右腿伸肌过强','不动','不动','10462、10461受体乘数','固定共同20ms滤波/50Hz；非逐时刻u拟合'],
        ['H05抑制不足试探','全局抑制乘数可能覆盖抑制DN','抑制源释放增益0.03→0.1','另试伸肌受体×0.5','不重写时间曲线'],
        ['H06消融旁路','DNg100→伸MN边效力0.2','固有参数不动','固有参数不动','读取原神经输出'],
        ['N14局部核心募集','不动','六个I1兴奋受体1→2','不动','不动'],
        ['M01后来AB募集','无同轮改变记录','无同轮改变记录','74MN gain×3/leak×0.8','另有M02标定，不可混为单因子'],
        ['M02幅值标定','不动','不动','不动','滤波160ms、40Hz尺度、逐通道gain'],
        ['M03/M04前腿对齐','无同轮改变记录','无同轮改变记录','明确10MN的gain/leak/NaP/bias','还同时改身体摩擦M09'],
        ['整个原R2→最终包','确有非MN变化，快照附录列全','确有非MN变化，目的/顺序不全','快照列出实际变化','补池、外部18路、身体弹簧/摩擦']])
    tx+='\n# 逐现象与试验：细胞、参数、依据和保留决定\n\n每张表是一次目的明确的试验或同一目的下的连续试探；不是一条包内现象“支持”就等于调参成功。N为神经现象，M为后来肌肉/身体调整，H为早期肌肉相关阶段。\n\n'
    for a in A:
        tx+=f'## {a["id"]}　{a["title"]}\n\n'
        step_reason={
            'N14':'实际只比较1、2、4。2已募集双侧且比4偏移小；没有搜索1–2之间的最小有效值。',
            'N10':'r1取2.5后右侧募集而左侧仍阈下，下一次取3.5。为什么增1而非更细步没有完整记录，不说成精确阈值。',
            'N09':'3000ms拖尾过长，再缩至2000ms；没有完整连续扫描，不称唯一最优清除常数。',
            'N04':'2改善oDN1但转向输出未被充分抑制，继续试4；仍未完成所有停止要求。',
            'N12':'先1.5可募集chief；抑制边取2仍有两腿残余，再取3.5。未证明3.5是最小有效值。',
            'H04':'RH取0.5后仍偏强，继续0.3，再对RM同样试0.3；该逐细胞候选后来被共享通路替代。',
            'H03':'由1试0.75/0.5，比较限位、真实角运动及均值对照；未完成所有后续验证。'
        }.get(a['id'],'只确认表中列出的幅度/候选值；缺少为何恰取这些数值、连续小步和完整回退的日志，不能补造梯度、精确阈值或最优性。')
        tx+=tab(['项目','详细记录'],[
            ['历史版本/图',a['stage']],['实际改动层',a['layer']],['具体细胞/通路',a['target']],
            ['先看到的异常或要求',a['observed']],['如何定位关键节点',a['localization']],
            ['选择此参数及方向的依据',a['direction_basis']],['幅度、下一步与停止依据',step_reason],['该轮未改的层/连带影响',a['other_layers']],
            ['同条件复查/干预',a['controls']],['实际结果',a['result']],['保留或拒绝',a['disposition']],
            ['依据的性质',a['rationale_provenance']],['记录出处',a['source']]])
        tx+=tab(['参数','旧值/起点','新值/尝试顺序','方向'],a['changes'])
    tx+='\n# 新核对：保留下来的上游细胞也确实变过\n\n'
    tx+=f'原R2与最终包有{snapshot_summary["shared_cells"]}个同ID细胞可逐值比较；其中{len(byid)}个参数向量不同，分为{len(changed_mn)}个MN与{len(changed_nonmn)}个非MN。本次是两快照比较，不能确定发生在哪轮、为什么修改，更不能全部归为肌肉拟合。\n\n'
    tx+=tab(['差异组','精确变化','怎样解读'],[
        [f'PFL2/PFL3，原R2共有{len(pfl)}个已变更','excitatory_receptor_gain 1→5','脑内细胞确实变化；缺逐轮原因，不能说为了某块肌肉'],
        [f'其他原R2非MN {len(other)}个','逐细胞CSV列旧/新值；典型gain1→0.5、抑制释放1→8、总释放1→20','源/中继有效参数一起改，不是MN；缺当时完整决策流水'],
        ['新增细胞','由模板/中位数初始化，不能跟原R2无ID的细胞作差','不是这些细胞曾被手调的证据'],
        ['source_notes旧文案','仍称old cells unchanged','与最终数组逐值比较不符；它可能只描述某一次扩图，不能作为最终全阶段结论']])
    tx+='全部180个变化细胞的逐参数旧值、新值、方向另附all_retained_cell_parameter_deltas.csv。下方逐肌肉表只把有实际直连边的这些上游列为“关联变化”；不据静态边证明它们当时活跃或有因果贡献。\n\n'
    tx+='方向解释也需分清乘积：对模型判为抑制的出边，源端抑制释放乘数8与总释放20共同进入事件幅度，合计为原对应乘积的160倍；同时靶兴奋增益0.5会降低这些源自身接收的兴奋。这里能明确计算潜在作用方向，但缺失的历史选择理由不能据公式补写。它也不是“所有细胞的参数只轻微偏移”。\n\n'
    tx+='\n# 逐肌肉：本轮到底改了MN还是VNC，上游变更与输出标定分开\n\n'
    tx+='每块肌肉均列出实际候选MN。**本轮进一步找到包内phenomena.json的完整24肌肉与74MN名单**；再对最终向量撤销已记录的M03/M04倍数，识别gain18、leak=1.32181835973签名，得到74个ID，与包内名单完全相同。所以下文能区分“当时24个直接选择目标”和“共享MN导致的连带通道”；仍不能恢复每次rate<15Hz筛选与回退的原始轨迹。上一版说名单不可列出不够准确，此处更正。\n\n'
    tx+=tab(['M01记录中的24个直接目标'],[(x,) for x in sorted(targeted24)])
    muscle_export=[]
    for leg in ['LF','RF','LM','RM','LH','RH']:
        tx+=f'## {leg}腿\n\n'
        for m in mapping:
            if m['leg']!=leg:continue
            mid=m['muscle_id'];pool=m['MN_indices'];ids=[str(neurons[i]['bodyId']) for i in pool]
            tx+=f'### {mid}\n\n'
            selected=[str(neurons[i]['bodyId']) for i in pool if i in inferred74]
            dsel=[b for b in ids if b in depids];lsel=[b for b in ids if b in levids]
            up=sorted(set().union(*(incoming[i] for i in pool))) if pool else []
            uptext='；'.join(f'{neurons[i]["bodyId"]}({neurons[i].get("type")},{neurons[i].get("superclass")})' for i in up) or '未发现与原R2相比参数变化的非MN直达输入；不排除更上游或新增细胞'
            signatures=collections.defaultdict(list)
            for i in up:
                b=str(neurons[i]['bodyId']);s='；'.join(z['parameter']+' '+fmt(z['R2_value'])+'→'+fmt(z['full_model_value']) for z in byid[b]);signatures[s].append(b)
            updelta=' / '.join('细胞'+','.join(bs)+'：'+s for s,bs in signatures.items()) or '无上述直接输入差异。'
            shared=sorted({mid2 for i in pool for mid2 in mn_to_muscles[i] if mid2!=mid})
            same_mn_text='；'.join(shared) if shared else '当前候选映射中无共享的其他通道。'
            unchanged=[b for b in ids if b in oi and b not in byid]
            acts=[]
            if selected:acts.append('M01签名MN：'+','.join(selected)+'；gain6→18、leak1.65227295→1.32181836（在M03/M04前）')
            if dsel:acts.append('M03 depressor：'+','.join(dsel)+'；按上表四项降低驱动，最终数值见下')
            if lsel:acts.append('M04 levator：'+','.join(lsel)+'；gain×1.35、leak×0.9，最终数值见下')
            if not acts:acts=['无该通道专属MN调节的可核对记录；最终池继承共享膜参数，不能因此说整个上游未调过']
            wired=mid in model['source_notes'].get('banc_tarsus_wiring',{}).get('filled_pools',{})
            gainold=oldmap.get(mid,{}).get('output_gain',1)
            layers='M01/M03/M04所述肌肉轮次没有额外DN/VNC同步修改记录。整个模型上游确有改变，但具体目的见快照限制。'
            if mid in external:interface='M07：实际身体u取AB；空MN池，最终output_gain不决定该外部输入。'
            else:interface=f'M02：原R2接口gain={gainold}；最终gain={m.get("output_gain",1)}。这是跨阶段差值，不知道每轮方向；共同滤波160ms/尺度40Hz。'
            geometry='RM关节弹簧M08会影响此腿；不是为该通道单独调肌肉参数。' if leg=='RM' else 'T1摩擦M09影响足端接触；非该通道独立神经收益。' if leg in ['LF','RF'] else '无该通道专属身体参数调节记录。'
            why='有神经池：按低驱动MN募集(M01)、平均幅值标定(M02)、前腿过屈对齐(M03/M04)分别解释；不把它们强行合成一个针对本肌肉的独立因果试验。' if pool else '空池不是MN不兴奋；无法靠增益激活，故用外部AB输入补工程回放。'
            tx+=tab(['调节层/依据','本肌肉的具体记录'],[
                ['候选MN（MaleCNS）',','.join(ids) or '空池'],['MN具体改动', '；'.join(acts)],
                ['M01是否直接选择本肌肉','是，列在原包24目标名单内' if mid in targeted24 else '未列在原包24目标内；若池内有74MN，则属共享MN连带影响，而非本肌肉单独定向选择'],
                ['与原R2的17项参数完全相同的池内MN',','.join(unchanged) or '无/空池；新增细胞不作原R2比较'],
                ['DN/VNC是否也为本肌肉调过',layers],['原R2→最终，直接输入该池的已变更非MN',uptext],
                ['这些直接上游具体改了什么',updelta],
                ['同一MN调整还会连带哪些肌肉',same_mn_text+' 这些池共享募集/发放，不能独立给每块肌肉安排MN参数；输出gain仍可逐通道不同。'],
                ['输出接口/外部u',interface],['是否补过映射', 'M06：BANC同源候选补池；不是调膜参数' if wired else '无M06补池记录；既有池仍为候选同源映射' if pool else '仍空池'],
                ['肌肉力学及身体',geometry+' 本轮无该肌肉force-length/force-velocity等常数单独重拟合记录。'],
                ['选择动作的依据',why],['独立验收程度','已有整组AB/quiet/身体结果；没有本肌肉单独的DN→VNC→MN因素分解或独立通过结论。']])
            delta_rows=[]
            for i in pool:
                b=str(neurons[i]['bodyId'])
                if b in byid:
                    for z in byid[b]:delta_rows.append([b,z['parameter'],fmt(z['R2_value']),fmt(z['full_model_value']),z['direction']])
            if delta_rows:tx+=tab(['MN ID','参数','原R2值','最终值','方向'],delta_rows)
            muscle_export.append({'muscle':mid,'leg':leg,'MN_ids':','.join(ids),'M01_signature_ids':','.join(selected),
                'M01_recorded_target24':mid in targeted24,
                'M03_ids':','.join(dsel),'M04_ids':','.join(lsel),'R2_output_gain':gainold,'final_output_gain':m.get('output_gain',1),
                'actual_drive':'AB外部' if mid in external else '神经池','direct_changed_nonMN_ids':','.join(str(neurons[i]['bodyId']) for i in up),
                'direct_changed_nonMN_parameter_changes':updelta,'shared_MN_other_muscles':';'.join(shared),
                'not_claimed':'静态上游关联不证明特定肌肉调参意图或功能贡献；无单通道因子分解'})
    writecsv('muscle_layer_actions_130.csv',muscle_export)
    tx+='\n# 对每个包内现象：有没有专门调，不能用验证代替调参\n\n'
    direct={4:'N12',22:'N18',37:'N12',38:'N12',48:'N01',49:'N01',56:'N14/N15/H02/H06',64:'N12',65:'N12',73:'N22（成年模板，不是全部单位募集完整复现）',76:'N20（仅前腿反相试探，不是三足协调）',82:'N12',83:'N17',84:'N11',92:'N08/N10（仅代理，不是完整自然活动）',93:'N10（尝试中继，不实现支撑门控）',94:'M03/M04（姿态修正，不是BRK角度门控）',95:'N21',98:'N22（单细胞模板校准）',99:'只可核对感觉刺激/背景反转与部分上游快照差异，完整专属调参流水缺失',109:'N21',125:'N19',126:'N09',127:'N01',128:'N01/N05',129:'N01',132:'N11/N17',133:'N12',137:'N04/N06/N08/N10',143:'N22',146:'H01/H03/M01/M02'}
    rows=[]
    for idx,(lit,fin) in enumerate(zip(ph['additional_literature_inventory'],ph['final_verification_146']),1):
        claim=lit.get('claim',{})
        title=(claim.get('fact') or claim.get('title_zh') or claim.get('id') or val(claim)) if isinstance(claim,dict) else claim
        rows.append([idx,title,direct.get(idx,'无本现象专属调参记录；可能仅刺激/消融/结构检查，不能补造细胞与方向'),fin.get('verdict','未列')])
    tx+=tab(['序号','现象','对应实际调节表/缺口','包内结论（非本次复跑）'],rows)
    tx+='\n# 关键限制与可复现文件\n\n'
    tx+='本版不提供“如果以后调应该怎么调”的替代方案。表中没有日志的初值、步长、精确时间顺序和唯一原因均不补造。原R2与最终模型的快照差异是本次新核对；用户后来包内的试验仍属于其记录，不能冒称本次重新完成。所有源、参数、差异与脚本身份见manifest.json。\n\n'
    tx+=tab(['附件','内容'],[['actions.json','全部操作的观察、定位、方向依据、控制、结果与出处'],['all_retained_cell_parameter_deltas.csv','所有原R2同ID细胞的逐参数快照差异'],['muscle_layer_actions_130.csv','130肌肉的分层调节与关联上游索引'],['snapshot_comparison.json','比较哈希、变更ID、74MN签名重建与明确跗节ID'],['build_report.py / action_catalog.py','只读提取与文档排版代码；不运行仿真']])
    tx+=f'原R2模型SHA256：{digest(args.r2)}。最终模型SHA256：{digest(mp)}。\n\n当前工作没有修改两份输入模型。原包下载：<https://github.com/linzhefeng24/Applepie/releases/download/new/flybody_male_full.zip>；历史R2包：<https://github.com/linzhefeng24/Applepie/releases/download/manual-r2-freebody-20261119/Manual_R2_FreeBody_Complete.zip>。\n'
    (R/'report.md').write_text(tx)
    css='''@page{size:A4;margin:16mm 14mm 17mm;@bottom-center{content:counter(page) " / " counter(pages);font-size:9pt;color:#687b8f}}
body{font-family:"Noto Sans CJK SC",sans-serif;font-size:9pt;line-height:1.65;color:#182b40;overflow-wrap:anywhere}h1{font-size:18pt;color:#194b70;page-break-before:always}h1.title{page-break-before:auto;font-size:24pt}h2{font-size:12pt;color:#194b70;break-after:avoid;margin-top:19pt}h3{font-size:10.5pt;color:#194b70;break-after:avoid}table{border-collapse:collapse;width:100%;margin:9pt 0 15pt;font-size:8.2pt;line-height:1.55}th,td{border:.5pt solid #cad7e2;padding:5pt;vertical-align:top;overflow-wrap:anywhere}th{background:#e7f0f7;text-align:left}thead{display:table-header-group}tr{break-inside:avoid}p{orphans:3;widows:3}a{color:#236b9b}code{font-family:inherit;font-size:8pt}#title-block-header{padding-top:18mm;padding-bottom:12mm;border-bottom:2pt solid #194b70}'''
    (R/'report.css').write_text(css)
    subprocess.run(['pandoc',str(R/'report.md'),'--standalone','--toc','--toc-depth=2','--css','report.css','-o',str(R/'report.html')],check=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page();html=(R/'report.html').read_text().replace('<link rel="stylesheet" href="report.css" />','<style>'+css+'</style>')
        page.set_content(html,wait_until='load');page.evaluate('document.fonts.ready')
        page.pdf(path=str(R/'Detailed_Tuning_Actions_Revised.pdf'),print_background=True,prefer_css_page_size=True,outline=True);browser.close()
    add_pdf_outline(R/'Detailed_Tuning_Actions_Revised.pdf')
    import fitz
    doc=fitz.open(R/'Detailed_Tuning_Actions_Revised.pdf');text='\n'.join(p.get_text() for p in doc)
    overflow=[]
    for i,p in enumerate(doc):
        for b in p.get_text('blocks'):
            if b[0]<-1 or b[1]<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1:overflow.append(i+1)
    qa={'pages':len(doc),'actions':len(A),'muscles':len(muscle_export),'inferred_74':len(inferred74),
        'compared_changed_cells':len(byid),'changed_MN':len(changed_mn),'changed_non_MN':len(changed_nonmn),
        'recorded_24_targets_found':sum(m['M01_recorded_target24'] for m in muscle_export),
        '74_signature_matches_source_ids':{str(neurons[i]['bodyId']) for i in inferred74}==recorded74,
        'collateral_channels_from_shared_MN':sum(bool(m['M01_signature_ids']) and not m['M01_recorded_target24'] for m in muscle_export),
        'all_action_headings':all(a['id'] in text for a in A),'blank_pages':[i+1 for i,p in enumerate(doc) if not p.get_text().strip()],
        'overflow_pages':sorted(set(overflow)),'replacement_chars':text.count('\ufffd'),'pdf_outline_entries':len(doc.get_toc())}
    assert qa['all_action_headings'] and not qa['blank_pages'] and not qa['overflow_pages']
    (R/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
    manifest={'scope':'Revised detailed manual-action audit; static snapshots, no new simulation or model changes','date':'2026-11-25',
        'source_code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'inputs':{'original_R2':{'sha256':digest(args.r2),'bytes':args.r2.stat().st_size},'final_model':{'sha256':digest(mp),'bytes':mp.stat().st_size},
        'user_package_source':'https://github.com/linzhefeng24/Applepie/releases/download/new/flybody_male_full.zip','user_package_sha256':'0450edb9313b1cd502ea4cc38ecd6efad34ffb482e7dd09dc614c225bd166846','sources':sources},
        'command':'python build_report.py --package /path/to/flybody_male_full --r2 /path/to/Manual_FreeBody/01_model/model.yaml',
        'software':{'python':sys.version,'numpy':np.__version__,'PyYAML':yaml.__version__},'random_seed':None,
        'limitations':['Historical decisions not fully logged','snapshot diffs cannot recover intention/order','74 MN IDs and 24 muscles are explicitly recorded and independently signature-checked; per-step screening traces remain missing','only direct changed inputs are enumerated; presence is not activity/causation'],
        'outputs':[{'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(R.iterdir()) if p.is_file() and p.name!='manifest.json']}
    (R/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(qa,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
