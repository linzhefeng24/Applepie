# 逐现象与逐肌肉手动调参：详细PDF

[下载PDF](Manual_Tuning_Detailed_Report.pdf)

本次是历史调参证据整理和最终参数静态提取，未进行新仿真、训练或模型修改。

PDF共93页，约1.4 MB。已检查146个条目标题齐全、无空白页、无文字越出页面，并抽查封面、参数表及现象表的中文显示。

- 正文：区分20 ms关节分段调u、神经驱动肌肉粗趋势、实验现象优先；逐项说明细胞/通路、参数方向、定位依据、步进、结果和保留/拒绝原因。
- 附录A：130个肌肉通道，逐个列出最终输出增益、MaleCNS MN候选ID、细胞参数组和外部AB驱动标记；18路外部AB不算神经生成。
- 附录B：最终模型全部不同的细胞参数向量，17项参数完整列出。最终值不反推为已知调节历史。
- 附录C：原包146个现象，保留要求、方法、观察、结论及较早记录差异；这些是包内记录，不是本次独立重跑146项。
- 附录D：原包关键试验摘要，保留成功、失败和临时试验。

源文档为[前次历史审计](../manual-tuning-method-audit-20261125/README.md)及[用户包](https://github.com/linzhefeng24/Applepie/releases/download/new/flybody_male_full.zip)，来源身份和输出哈希见manifest.json。没有逐次流水或没有有效调节结果的现象会明确保留缺口，不补造参数。

## 重新生成

安装Python依赖 `numpy PyYAML PyMuPDF playwright`，系统安装pandoc、Chromium与Noto CJK字体。解压上述原包后执行：

```bash
python research/manual-tuning-pdf-20261125/build_report.py --package /path/to/flybody_male_full
```

PDF使用本地HTML和字体生成，无需访问网页。受限沙箱内Chromium可能不能启动，需要有浏览器运行能力的本地环境。

## 附带文件

`report.md`为完整可编辑正文；`report.html`和`report.css`为排版源；`muscles_130.csv`与`cell_parameter_groups.csv`提供可检索数值；`phenomena_146_source.json`保留逐现象原字段；`qa.json`记录条目及页面完整性；`manifest.json`记录输入/输出身份与生成环境。

生成过程曾遇到两项文档工具问题：部分现象的claim为字符串而非字典，现已兼容；Chromium直接命令行打印在当前环境未完成，现改用Playwright加载后打印。它们不是神经/物理实验失败，也没有改变输入模型。
