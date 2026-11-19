# 全现象逐条验证与缺失结构补全

保留原4159细胞候选。146条原始现象逐条保存在 `brain.json`，不是146个独立实验。官方身份与别名覆盖见 `identity_registry.json`；新增细胞、参数借用及连接的出处分别见 `new_neurons.json`、`parameter_priors.json`、`source_manifest.json`。

结构扩展仅从同版本MaleCNS官方注释与significant-only连接表取实际细胞/边：补全VNC motor集合（708，包含非腿运动神经元，不能全称六腿MN）、所选腿神经入口的726个本体感觉细胞、chief9A缺失同型细胞，以及DNb08通路E4/E5缺失细胞。旧4159个细胞全部参数、旧连接及肌肉候选映射保留。新增参数是借用先验，不是实测。

P9=DNp09，FG/BB/BRK/BON1等采用有来源的交叉表并作类型检查；BPN仅作为CL210_a候选群。发现MANC编号13157在官方注释中同时映射到IN09A012和SNpp41，不能用字典覆盖后当成唯一身份。chief9A按类型、胸节及左右核验。FeCO明确hook/claw/club注释仅覆盖右后腿33个细胞；不把其余感觉细胞自动填成同样功能。

目前源码构建模型在 `cache/expanded_model.yaml`。所有旧数组不变性检查在 `build_report.json`。仍需为新模型重新进行动态检验，不能沿用旧模型通过状态。LUL130/MF14/MAN/CxHP8等的精确身份和感觉/行为/受体机制分别标明，不以虚构细胞填补。
