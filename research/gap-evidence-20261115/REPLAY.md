# 复跑和来源定位

神经环境版本见相邻conductance的requirements.txt。公开结构原始输入通过既有草稿Release恢复，来源/大小/SHA在该目录data/public-input-release-verified.json；不重复上传原始数据库。

```
python search_public.py
python fetch_fulltexts.py
python extract_sensory_routes.py
python build_brake_extension.py
```

前两项需普通公开网络。后两项默认读取`/workspace/exports/malecns-source`已验证的原始feather；可在程序常量B改为已恢复目录。两边路径CSV为gzip，身份CSV与路径表都带同一MaleCNS命名空间。

从相邻conductance目录执行：

```
python pulse_neural_panel.py BPN+P9 configs/manual-neural-bank-r9.json unified-r9-gap-validation results/mcns-unified
python pulse_neural_panel.py P9 configs/diagnostic-DNg97-coupling18.json unified-r9-coupling18-diagnostic results/mcns-unified
python pulse_neural_panel.py P9+BB configs/diagnostic-DNg97-coupling18.json unified-r9-coupling18-diagnostic results/mcns-unified
python pulse_neural_panel.py PFL3L configs/diagnostic-E-minus10.json r9-E-minus10 results/mcns-unified
python pulse_neural_panel.py PFL3L configs/diagnostic-E-plus10.json r9-E-plus10 results/mcns-unified
```

P9效力试验分别以P9、P9+BB、P9+FG执行，配置`diagnostic-P9-DNg97-efficacy07.json`，标签`r9-P9-efficacy07-diagnostic`，同一mcns-unified图。

新增运动端试验：

```
python pulse_neural_panel.py control configs/manual-neural-bank-r9.json brake-extension-r9 results/mcns-brake-extension .0125 annotated-MN
python pulse_neural_panel.py MDN configs/manual-neural-bank-r9.json brake-extension-r9 results/mcns-brake-extension .0125 annotated-MN
python pulse_neural_panel.py BRK configs/manual-neural-bank-r9.json brake-extension-r9 results/mcns-brake-extension .0125 annotated-MN
python pulse_neural_panel.py MDN+BRK configs/manual-neural-bank-r9.json brake-extension-r9 results/mcns-brake-extension .0125 annotated-MN
```

随后从本目录运行`diagnose_routes.py`、`review_extended_brake.py`、`trace_brake_relays.py`、`summarize_validation.py`。额外中继探针的完整脉冲必须与原始BRK一致，否则程序拒绝认定为相同活动。主图符号/无符号子矩阵一致性由build脚本显式检查。

本轮14个本地网络积分均确定性，无随机抽样。`.github/workflows/reproduce-brake-extension.yml`在正常GitHub runner独立复跑四条件；远程结果不是本地原始NPZ的副本，来源与SHA分别记录。

E2/I2因果检验：从conductance目录执行 `python trace_manual_network.py expanded-shared-extensor-direct-DN-weak-E2-I2-silenced`，随后本目录执行 `compare_E2_I2.py`。程序验证与既有E2条件参数/图/驱动完全一致，只增加I2消融。
