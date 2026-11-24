"""Build a Chinese, source-audited PDF. Reads artifacts; never runs a simulation.

Usage: python build_report.py --package /path/to/flybody_male_full
Requires PyYAML, NumPy, pandoc, Chromium, Playwright, Noto CJK fonts, and PyMuPDF for QA.
"""
from pathlib import Path
import argparse, base64, collections, csv, hashlib, io, json, os, subprocess, sys
import numpy as np
import yaml

R = Path(__file__).resolve().parent
ROOT = R.parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def txt(v):
    if v is None:
        return '未提供'
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)

def cell(v):
    return txt(v).replace('|', '／').replace('\n', '<br>').replace('`', '')

def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(cell(x) for x in row) + ' |' for row in rows]) + '\n\n'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', type=Path, required=True)
    args = ap.parse_args()
    p = args.package
    modelpath = p / '01_model/model.yaml'
    model = yaml.load(modelpath.read_text(), Loader=yaml.CSafeLoader)
    phenomena = json.loads((p / '03_phenomena/phenomena.json').read_text())
    with np.load(io.BytesIO(base64.b64decode(model['neural']['cell_parameters']['payload'])), allow_pickle=False) as z:
        params = z['values'].copy()
    columns = model['neural']['cell_parameter_columns']
    neurons = model['neural']['neurons']
    mapping = model['neuromuscular']['mapping']
    external = set(model['neuromuscular']['external_drive']['muscle_ids'])
    # Deterministic shared-row identities by first occurrence, no model mutation.
    groups, groupids = [], []
    lookup = {}
    for row in params:
        key = row.tobytes()
        if key not in lookup:
            lookup[key] = len(groups) + 1
            groups.append(row)
        groupids.append(lookup[key])
    muscle_rows = []
    for i, m in enumerate(mapping):
        ids = [str(neurons[j]['bodyId']) for j in m['MN_indices']]
        sets = [groupids[j] for j in m['MN_indices']]
        muscle_rows.append({'number': i+1, 'muscle_id': m['muscle_id'], 'leg': m['leg'],
            'actuator_index': m['actuator_index'], 'drive': '外部AB' if m['muscle_id'] in external else '候选神经池',
            'output_gain_final': m.get('output_gain',1), 'MaleCNS_MN_ids': ','.join(ids),
            'parameter_groups_in_same_order': ','.join('P'+str(x) for x in sets),
            'target_label': m.get('target_label',''), 'mapping_status': m.get('status',''),
            'mapping_source': m.get('source',''), 'historical_per_channel_change': '缺逐轮流水；最终值不等于调整方向'})
    with (R/'muscles_130.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(muscle_rows[0]),lineterminator='\n');w.writeheader();w.writerows(muscle_rows)
    with (R/'cell_parameter_groups.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['group','cell_count']+columns)
        for j,row in enumerate(groups,1):w.writerow(['P'+str(j),groupids.count(j)]+row.tolist())
    final = phenomena['final_verification_146']
    historical = {x['id']:x for x in phenomena['additional_literature_inventory']}
    assert len(mapping)==130 and len(external)==18 and len(final)==146
    (R/'phenomena_146_source.json').write_text(json.dumps({'provenance':'User-package claims and recorded tests, not 146 new independent validations',
        'source_sha256':sha(p/'03_phenomena/phenomena.json'),'final_distribution':phenomena['final_distribution'],
        'literature_inventory':phenomena['additional_literature_inventory'],'final_verification_146':final,
        'key_checks_full_model':phenomena['key_checks_full_model']},ensure_ascii=False,indent=2)+'\n')
    text = '''---
title: "果蝇神经—肌肉模型：逐现象与逐肌肉手动调参详表"
author: "Applepie 项目 · 历史记录与最终模型审计"
date: "2026年11月25日"
lang: zh-CN
---

# 阅读说明与范围

本报告回答：针对不同实验现象、肌肉激活或关节轨迹，分别选择了哪些细胞、通路和参数，为什么往某方向改，试过多少，最后保留还是失败。

**本次工作是文档整理和静态参数提取，没有新跑神经或身体仿真，没有更新任何模型参数。** 已有记录、用户上传包中的结果、此前独立重跑结果和方法建议必须区别阅读。完整实验复现、神经定性响应和软件接口可运行也不是同一层次。

“方向确定”表示记录能够确认某次试验实际向上或向下调节，不代表该方向在所有网络状态都有效；“最终值”表示可从当前模型精确读取，不表示知道其完整调节历史。没有记录的逐次操作不会据最终参数倒推补写。

正文按任务解释策略；附录A完整列出130个肌肉通道与MN候选池及最终增益；附录B列出全部共享细胞参数组；附录C逐条保留146个现象的文献要求、包内方法、观察和结论；附录D保留包内关键试验摘要。附录中的旧/新结果若不一致，会并列标注，不将旧结果自动迁移到最终模型。

# 调参对象与历史版本

| 阶段 | 改什么 | 目标与停止依据 | 记录边界 |
|---|---|---|---|
| 早期20 ms分段手调 | 分段肌肉控制u(t) | 同一段内反复修关节末端偏差，再推进下一段 | 缺完整逐次增量/回退流水 |
| 神经驱动肌肉粗趋势 | MN兴奋性、通路效力、脉冲到u的接口 | 通路实际发挥作用，肌肉幅值/时间趋势与不对称性 | 不是每个通道都有独立调节历史 |
| 实验现象优先 | 特定细胞家族、通路或时间机制 | 对应刺激/消融条件下具体神经响应 | 多数不是完整实验定量复现 |
| 后来上传的全量扩展包 | 上述部分机制，以及输出增益和身体参数 | 包内曾使用轨迹不退化规则 | 与实验现象优先要求有优先级差别 |

旧MANC区域图、MaleCNS裁剪图与后来26,885细胞模型是不同上下文。不能混用EM ID、继承消融结论或把分阶段参数连成一个不存在的连续优化。

# 神经现象：具体调节索引

| 目标 | 对象 | 参数方向与试验步 | 结果与状态 |
|---|---|---|---|
| I1募集 | 六个IN16B036；T1 801884/803183 | 靶兴奋受体增益1→2→4 | T1脉冲0/0→15/14→18/13；留2作诊断候选 |
| E1消融后抽查胫节MN静默 | 当时MANC图DNg100→胫节伸MN；10339→11706是定位例 | 共享末端效力降到0.2 | 12个抽查MN静默；全体仍11个活动 |
| E2消融旁路 | 11月19日MaleCNS DNg100→MN | 末端×0.5/0.25；MN兴奋增益6→3/1.5 | 其他DN补偿；未纳入主候选 |
| BRK持续中继 | AN19A018→IN07B001，800051/800053 | 通路效力1→2.5→3.5 | r2双侧晚期仍放电；不是身体刹车通过 |
| BON1长拖尾 | IN27X001候选家族 | 有效Ca清除100→3000→2000 ms | 2000比3000更合适；观测模型未标定 |
| BB抑制不足 | BB源家族 | 抑制释放先2再4 | 改善部分响应；P9相关仍不完整 |
| 胞体被抑制但轴突仍发放 | 泛化胆碱能DN跟随细胞 | 轴突偏置+5→0 pA；命名源另设 | 避免轴突独立偏置掩盖胞体抑制 |
| 左右转向神经响应 | PFL2/PFL3与命名指令组 | PFL偏置+5 pA；部分指令组K×0.8 | 组合参数有左右响应；单项贡献未隔离 |
| motor募集chief | 六腿chief9A候选 | 兴奋增益增至1.5 | 募集成功，同时Web抑制失效 |
| Web抑制chief | 已有DNg74/Web→chief | 末端增益2→3.5 | 稳定阶段六腿chief均受抑制 |
| 重复感觉刺激适应 | Ti flexor MN，后来包 | SK×5/Ca×2，再×10/×4 | 中间回弹，未采用 |
| DNg13相对潜伏期 | DNg13，后来包 | C×2/leak×0.5，再C×4/leak×0.25 | MN包络变慢但相对顺序仍错，未采用 |
| 慢节律时间尺度 | 全局抑制突触 | 衰减30→60 ms | 变慢；机制干预，非最终参数修改 |
| LF/RF反相 | DNg105R13130/DNg93R10717→LF MN | 75条输入效力×4/×10 | 仍同相，未采用 |
| 9A或13B单独输出 | 各自家族分别试 | leak×0.85、输入×2、释放×2 | 源强放电而MN零，未采用 |

# 肌肉与身体：具体调节索引

| 对象 | 问题 | 实际参数方向 | 是否保留/边界 |
|---|---|---|---|
| 24个低驱动肌肉池内74个MN | 招募不足 | 兴奋受体×3、胞体漏电×0.8 | 包内保留；两个参数一起改，单项贡献未隔离 |
| 112个神经驱动肌肉 | 幅值标定 | AB u均值/模型均值作有限幅增益更新 | 缺逐轮逐肌肉改动流水；附录A提供最终值 |
| T1左右tarsus depressor MN | 下关节过屈 | 输入×0.65、leak×1.3、NaP×0.7、偏置−0.25 pA | 最终包保留，多参数共同改变 |
| T1左右tarsus levator MN | 增强相反驱动 | 输入×1.35、leak×0.9 | 最终包保留 |
| RF下关节较早候选 | 过屈 | depressor输出接近0；levator×4；tibia屈肌×0.2、伸肌×2 | 局部伸直而整体变差，拒绝 |
| LBL40下游MN | 源强、下游弱 | 52条至MN的出边×10 | T3屈MN活动，因旧轨迹规则拒绝；非全是屈肌专属边 |
| 18条无MN池通道 | 结构映射缺口 | 外部AB u直接驱动 | 不是神经网络生成 |
| RM tarsus被动关节 | 过屈 | stiffness=1、springref=−0.14、damping=0.05 | 身体参数，不是肌肉/神经参数 |
| T1 tarsus/claw接触 | 滑移与支撑 | 摩擦0.5→2.0 | 身体接触参数，不是神经拟合 |

'''
    audited=(ROOT/'research/manual-tuning-method-audit-20261125/README.md').read_text()
    # Keep the full audited discussion, including failures, limits, and source paths.
    text += '\n# 详细依据、定位逻辑与逐次决策\n\n' + '\n'.join(('##'+line[1:] if line.startswith('# ') else '#'+line if line.startswith('## ') else line) for line in audited.splitlines()) + '\n'
    text += '\n# 附录A：全部130个肌肉通道\n\n'
    text += f'从最终模型直接提取：{len(mapping)}通道；{len(external)}条外部AB驱动，其余112条有候选神经池。全局滤波时间={model["neuromuscular"]["filter_tau_ms"]} ms，rate_scale={model["neuromuscular"]["rate_scale_Hz"]} Hz。最终输出增益不能反推出历史上是增大还是减小；外部AB通道的神经输出增益不能解释其实际直接输入。\n\n'
    text += 'MN ID均为MaleCNS；P编号与同一行MN ID逐一对应，可在附录B读取17项细胞参数。候选池是跨动物/类型层面的估计，不能当作逐MN到单肌肉的确认解剖。肌肉名含FlyMimic字样也不表示六腿均为原版FlyMimic解剖。\n\n'
    for leg in ['LF','RF','LM','RM','LH','RH']:
        text += '## '+leg+'\n\n'
        rows=[]
        for m in muscle_rows:
            if m['leg']==leg:
                rows.append([m['number'],m['muscle_id'].replace('_','_<wbr>'),m['drive'],m['output_gain_final'],m['MaleCNS_MN_ids'] or '空池',m['parameter_groups_in_same_order'] or '无'])
        text += table(['序号','肌肉通道','驱动来源','最终增益','MN ID','参数组'],rows)
    text += '\n# 附录B：最终模型共享细胞参数组\n\n'
    text += f'{len(neurons):,}个细胞、{len(columns)}个参数列、{len(groups)}组不同参数向量。P编号仅为本报告按首次出现顺序分配，非生物学分类；同参数不表示同一细胞类型。这些是最终保存值，未测/手调身份不能只靠数值判断。\n\n'
    text += table(['列','原始参数名','说明'],[(i,k,{
        5:'靶端兴奋受体增益',6:'源端抑制释放增益，不是靶受体增益',12:'源端总释放增益',
        8:'SK乘数',10:'轴突偏置电流',16:'有效钙清除时间'}.get(i,'单位见原始参数名；记录值，不反推生理测量')) for i,k in enumerate(columns)])
    for indices in [list(range(0,6)),list(range(6,12)),list(range(12,17))]:
        text += '## 参数列 '+','.join(map(str,indices))+'\n\n'
        text += table(['组','细胞数']+[str(i) for i in indices],[(f'P{j}',groupids.count(j))+tuple(f'{row[k]:.9g}' for k in indices) for j,row in enumerate(groups,1)])
    text += '\n# 附录C：146个现象逐条保留\n\n'
    text += '**以下是用户包的文献与试验记录，不是本次独立重跑146项。** final_verification_146与较早inventory可能来自不同参数阶段，最终模型哈希存在也不意味着每条历史结果都以该哈希执行。正文有具体手调记录的才给出确定改动，其余条目不能臆造参数方向。\n\n'
    text += '包内分类计数（照录，不能当成本次审计结论）：'+txt(phenomena['final_distribution'])+'。支持/部分支持与完整实验复现有区别；部分状态只支持模型功能或神经代理。\n\n'
    for item in final:
        ident=item['id'].strip('`'); old=historical.get(ident,{})
        claim=old.get('claim',{})
        if not isinstance(claim,dict):
            claim={'fact':claim,'tier':old.get('tier','未列出'),'source':old.get('source','未列出')}
        text += f'## C{item["idx"]:03d}　{old.get("neurons",ident)}\n\n'
        rows=[('条目ID',ident),('细胞／结构',old.get('neurons','未列出')),
              ('现象要求',claim.get('fact','未列出')),('量化要求',claim.get('quant')),
              ('证据层级与来源',str(claim.get('tier','未列出'))+'；'+str(claim.get('source','未列出'))),
              ('包内方法',item.get('method','未列出')),('包内后期观察',item.get('observation','未列出')),
              ('包内后期结论',item.get('verdict','未列出'))]
        if old.get('final_observation') and old['final_observation']!=item.get('observation'):
            rows.append(('较早记录，非当前复跑',old['final_observation']))
        if old.get('final_verdict') and old['final_verdict']!=item.get('verdict'):
            rows.append(('较早结论',old['final_verdict']))
        rows.append(('对应确定调参','仅在正文已列出试验时成立；本条记录本身不提供可唯一追溯的逐细胞参数更新流水'))
        text += table(['字段','内容'],rows)
    text += '\n# 附录D：包内关键试验摘要原字段\n\n以下照录关键字段，属于用户包历史记录。某些强结论是包内作者解释，不等于本次审计已确认；因果外推边界以正文为准。\n\n'
    for key,value in phenomena['key_checks_full_model'].items():
        text += '## '+key+'\n\n'
        if isinstance(value,dict):text += table(['字段','记录'],list(value.items()))
        else:text += txt(value)+'\n\n'
    text += '\n# 来源、版本与复现本报告\n\n'
    text += f'最终神经模型SHA-256：{sha(modelpath)}。\n\n原始包：<https://github.com/linzhefeng24/Applepie/releases/download/new/flybody_male_full.zip>；其身份见同目录manifest.json。\n\n'
    text += '详细历史审计：<https://github.com/linzhefeng24/Applepie/blob/e46cec25517c2bd002ff84f5562a5d6ebb5c419d/research/manual-tuning-method-audit-20261125/README.md>。该目录evidence.json列出15份历史代码/参数/结果的SHA-256。\n\n'
    text += '重建命令：`python build_report.py --package /path/to/flybody_male_full`。无随机数、无训练、无仿真；输出CSV为最终静态值。生成脚本、Markdown、HTML、PDF、CSV和状态源JSON一并保存。\n'
    (R/'report.md').write_text(text)
    css='''@page {size:A4; margin:17mm 14mm 18mm; @bottom-center {content:counter(page) " / " counter(pages);font-size:9pt;color:#697386;}}
body{font-family:"Noto Sans CJK SC",sans-serif;color:#18243a;font-size:9pt;line-height:1.65;overflow-wrap:anywhere}
h1{font-size:19pt;color:#153c65;margin-top:24pt;page-break-before:always}h1.title{page-break-before:auto;font-size:25pt}
h2{font-size:12pt;color:#1c527c;margin-top:17pt;break-after:avoid}h3{font-size:10.5pt;break-after:avoid}
table{width:100%;border-collapse:collapse;margin:10pt 0 16pt;table-layout:auto;font-size:8pt;line-height:1.5}
th,td{border:0.5pt solid #cbd5e1;padding:5pt 6pt;vertical-align:top;overflow-wrap:anywhere}th{background:#e8f0f8;text-align:left}thead{display:table-header-group}tr{break-inside:avoid}a{color:#205b8b;text-decoration:none}code{font-family:"Noto Sans CJK SC",sans-serif;font-size:8pt;background:#f1f5f9}p{orphans:3;widows:3}#title-block-header{padding:22mm 0 12mm;border-bottom:2pt solid #205b8b}.subtitle{font-size:14pt}
'''
    (R/'report.css').write_text(css)
    subprocess.run(['pandoc',str(R/'report.md'),'--standalone','--toc','--toc-depth=1','--css','report.css','--metadata','pagetitle=逐现象与逐肌肉手动调参详表','-o',str(R/'report.html')],check=True)
    env=os.environ.copy();env['XDG_CACHE_HOME']='/tmp/applepie-pdf-cache'
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,env=env,
            args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files'])
        page=browser.new_page()
        # Typeset the local document in memory; no file URL or remote page needed.
        html=(R/'report.html').read_text().replace('<link rel="stylesheet" href="report.css" />','<style>'+css+'</style>')
        page.set_content(html,wait_until='load',timeout=60000)
        page.evaluate('document.fonts.ready')
        page.pdf(path=str(R/'Manual_Tuning_Detailed_Report.pdf'),print_background=True,prefer_css_page_size=True)
        browser.close()
    import fitz
    doc=fitz.open(R/'Manual_Tuning_Detailed_Report.pdf'); full='\n'.join(page.get_text() for page in doc)
    checks={'page_count':len(doc),'muscles':len(mapping),'external_AB':len(external),'phenomena':len(final),
        'parameter_groups':len(groups),'all_146_entry_headings_present':all(f'C{i:03d}' in full for i in range(1,147)),
        'replacement_character_count':full.count('\ufffd'),'blank_pages':[i+1 for i,page in enumerate(doc) if not page.get_text().strip()]}
    assert checks['all_146_entry_headings_present'] and not checks['blank_pages']
    (R/'qa.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    manifest={'scope':'Document creation and static extraction only; no simulations or parameter changes',
        'date_client':'2026-11-25','source_code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'input_release':{'url':'https://github.com/linzhefeng24/Applepie/releases/download/new/flybody_male_full.zip','bytes':356569241,'sha256':'0450edb9313b1cd502ea4cc38ecd6efad34ffb482e7dd09dc614c225bd166846'},
        'inputs':[{'name':str(q.relative_to(p)),'bytes':q.stat().st_size,'sha256':sha(q)} for q in [modelpath,p/'README.md',p/'03_phenomena/phenomena.json']],
        'command':'python build_report.py --package /path/to/flybody_male_full','seed':None,
        'software':{'python':sys.version,'numpy':np.__version__,'PyYAML':yaml.__version__,'PyMuPDF':fitz.__doc__.splitlines()[0:2]},
        'outputs':[{'name':q.name,'bytes':q.stat().st_size,'sha256':sha(q)} for q in sorted(R.iterdir()) if q.is_file() and q.name not in {'manifest.json'}]}
    (R/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(checks,ensure_ascii=False));print('PDF bytes:',(R/'Manual_Tuning_Detailed_Report.pdf').stat().st_size)

if __name__=='__main__':main()
