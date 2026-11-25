# 手调思路与具体动作：分层修订版

[下载详细PDF](Detailed_Tuning_Actions_Revised.pdf)

本版针对用户指出的缺项重写。主体为41张操作决策表，以及130个肌肉通道的分层核对表，不用“现象观察很多”和“最终参数很多”代替调参过程。

每张操作表说明：历史图/版本、具体细胞或通路、先看到的异常、如何定位、为何选这个参数和方向、旧值/新值/尝试顺序、幅度与停止依据、是否动过其他层、对照、结果、保留或撤回、记录出处。缺失的逐次流水不补造。

逐肌肉表分别列：

- MN候选ID、实际MN参数变化、与原R2完全相同的MN。
- 是否在原包24个直接目标内，或只是共享MN的连带影响。
- 同轮有无针对该肌肉的DN/VNC调节记录。
- 实际直接连到该MN池、且快照参数已变化的非MN细胞ID、类型及逐参数旧/新值。这只是静态上游关联，不证明当时活跃、因果贡献或修改目的。
- 肌肉输出gain、外部AB来源、映射补充、相关身体参数分别说明。
- 共享同一MN的其他肌肉，避免把耦合通道说成各自独立优化。

## 新核对与更正

1. 原R2与最终模型共有3988个同ID细胞可比；180个向量不同，其中82个MN、98个非MN。完整差异可下载CSV。
2. 在原包 `03_phenomena/phenomena.json → key_checks_full_model.pathway_excitability_tune` 找到完整24肌肉与74MN名单。它与独立参数签名重建完全一致，纠正前版“不能列出名单”的说法；逐轮筛选轨迹仍未恢复。
3. 74MN募集调整与10个跗节MN调整有2个重叠，合计82个MN。24个直接目标之外，另5个通道因共享这些MN而连带受影响。
4. 部分早期代码采用固定神经候选、自动数值拟合输出gain及按分数选解，不能统称“全程纯手调”。后来逐路径手动诊断与这些流程分别记录。
5. 用户后来包中的试验是包内历史记录，本次仅静态读取、核对及排版，没有运行新的神经/身体实验。

## 文件

- `report.md` / `report.html` / `report.css`：可编辑正文与排版。
- `actions.json` / `action_catalog.py`：41个操作记录、依据、边界及出处。
- `all_retained_cell_parameter_deltas.csv`：所有原R2同ID细胞的逐参数差异。
- `muscle_layer_actions_130.csv`：130肌肉的分层核对与共享池关系。
- `snapshot_comparison.json`：输入模型哈希、变化ID、明确24/74名单及一致性。
- `qa.json` / `manifest.json`：页面/条目检查、软件与输入输出身份。

## 重建

需要Python的numpy、PyYAML、PyMuPDF、playwright，系统pandoc、Chromium和Noto CJK字体。

```bash
python research/detailed-tuning-actions-20261125/build_report.py \
  --package /path/to/flybody_male_full \
  --r2 /path/to/Manual_FreeBody/01_model/model.yaml
```

用户新包：[Release new](https://github.com/linzhefeng24/Applepie/releases/download/new/flybody_male_full.zip)。原R2：[历史完整包](https://github.com/linzhefeng24/Applepie/releases/download/manual-r2-freebody-20261119/Manual_R2_FreeBody_Complete.zip)。本次未修改任何输入模型。
