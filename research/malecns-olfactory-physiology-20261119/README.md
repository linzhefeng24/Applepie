# MaleCNS嗅觉结构与成年细胞生理约束

2026-11-19，正在建立结构和参数证据基础。本目录不是已完成校准的全嗅觉仿真。

`extract_network.py` 已实际读取并SHA256核对MaleCNS v1.0原始注释、递质及筛选连接表，提取8,286个候选细胞、1,492,168个有向细胞对、6,411,933个解剖突触计数。包括ORN2639、PN686、LN420、KC4064、MBON97、APL2、ALIN24、ALON14和340个接触KC/MBON的DAN候选。候选范围较宽，不能将全部DAN自动等同于目标气味的教学单元。

`neurons.csv` 保存原始bodyId、类型、脑侧、跨数据集类型注释和递质共识；`group-connectivity.csv`保存逐组连接计数；`network-audit.json`保存运行命令、依赖版本、范围与输出哈希；`sources.json`记录官方输入URL、大小和哈希。注释表211577行包含超出已连接重建网络的body，不能把行数当作有效全CNS神经元数。连接表为minconf0.5 significant-only，缺边不代表真实不存在；递质预测未直接转换成固定符号。

完整提取边在忽略目录`cache/edges.npz`，不提交大型二进制；可由上述脚本从官方原始表重建。需要Python、numpy、pandas、pyarrow。实际运行命令见audit。

动力学证据与参数表正在补充，未开始网络参数拟合或完整仿真；不复用旧行走模型的生理参数。
