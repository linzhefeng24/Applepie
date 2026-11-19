# 手调 R2 的外部评价复核及连接组扩展

原始 R2 不修改。这里是独立的候选扩展，不取代已发布手调包。

## 已核实的缺口

- 外部记录的 146 行保存在 `external_observations_146.tsv`，原判定属于外部 AI 报告，未冒充本轮实测。它们并非 146 个独立实验。
- 官方注释确认此前提出的 144 个细胞全部可找到且不在原模型。
- 另发现论文核心类型缺失 15 个胸节同型细胞。首阶段补入后另核查论文 I2=IN19A007、E3=IN19B012 也缺失，再补入各 6 个。因此最终候选共新增 171 个细胞，3988 → 4159，新增 14911 条有向连接记录。159 细胞首阶段保留在 Git 历史与 `build_stage_159.json`，没有冒充最终实验。新增连接仅使用两个端点均入选的官方 significant-only 数据。
- 作者 CoreCPG 原始配置及索引表可将 MANC 10707/11751/13905 对应到 MaleCNS 800173/800863/801884。它们分别属于 IN17A001/INXXX466/IN16B036；左右 T1 对应细胞原来均缺失。不能将已有其他胸节同型细胞当成这些确切细胞。
- 更正外部评价见 `review.json`；全交叉表见 `paper_core_crosswalk.json`。

## 参数与限制

`parameter_priors.json` 逐细胞记录模板的具体 bodyId 和类型。新增膜参数是借用先验，不是成年实测标定。原模型所有细胞参数、连接、肌肉映射和刺激保持不变；构建时逐数组断言。Glu 抑制符号仍是明确的受体假设，单独做零符号敏感性实验，不声称生理已确认。

显示坐标仅为分层示意，没有真实 EM 形态，也没有恢复中央复合体环的角度拓扑。补入 EPG/Delta7 不等于复现罗盘活动。候选的局部实验不能证明真实行走或全部实验现象。

## 重建与运行

使用已发布完整手调包解压目录（含 `01_model`、`02_code`）：

```bash
python build.py --package /path/to/Manual_FreeBody
python experiment.py quiet DN_drive core_silenced new_glutamate_zero
```

`build.py` 默认使用本仓库此前恢复的包。`experiment.py` 当前同样默认该目录；可设置 `MANUAL_R2_PACKAGE` 指定自己的解压目录。依赖原包 Python 环境与 numpy/PyYAML；重新提取官方源数据时额外需要 pyarrow。

`extension_delta.npz`、`new_neurons.json`、参数来源表是完整可重建增量；无需重复下载 502 MB 连接表。生成模型在 `cache/extended_model.yaml`。`source_manifest.json` 记录原始来源及哈希，`build_report.json` 记录模型哈希和不变性检查。

本轮实验从初始神经状态重算 1600 ms，原步长 0.0125 ms；不重启已停止的 BPTT 训练。结果分实验保存在 `results/`，含输入事件、覆盖参数、原始脉冲、核心电位/电流、电导及肌肉 u(t)。`core_release_x2` 是手动候选，不是自动优化结果，也不默认选为最佳。
