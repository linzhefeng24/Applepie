# 果蝇嗅觉建模资料：结构、输入、生理、学习与代码

检索日期：2026-11-19。对象为成年果蝇嗅觉系统，优先支持ORN→嗅叶→PN→KC/APL→MBON/DAN。没有开展新仿真，没有声称已恢复一套完整、逐细胞生理标定的模型。推荐路线为研究判断，不是论文已验证结论。

## 优先阅读与可落地用途

| 模块 | 原始资料 | 可以约束 | 限制 |
|---|---|---|---|
| 外周与身份总表 | Benton等2025，An integrated anatomical, functional and evolutionary view of the Drosophila olfactory system，DOI 10.1038/s44319-025-00476-8 | 受体、感器、ORN及嗅小球的对应关系，更新的通路注释；Dataset EV1整合表、EV2附加资源 | 身份和解剖功能整合，不是完整的动态输入库；不同数据项有各自来源与确定程度 |
| 气味响应输入 | Münch/Galizia2016，DoOR2.0，DOI 10.1038/srep21841 | 气味×响应通道的整合响应矩阵、受体调谐模式和原研究关联 | 归一化/整合值不直接等于绝对Hz；不能当成所有浓度、时序和新受体均完整；未测不应填作无响应 |
| 原始受体电生理 | Hallem/Carlson2006，Coding of odors by a receptor repertoire，DOI 10.1016/j.cell.2006.01.050 | 受体响应谱，锚定气味输入 | 受体、气味、浓度及测量条件有覆盖边界；本次核对书目信息，未阅读全文 |
| ORN动态 | Nagel/Wilson2011，Biophysical mechanisms underlying olfactory receptor neuron dynamics，DOI 10.1038/nn.2725 | 转导与脉冲输出的动态、适应 | 不能仅靠稳态DoOR向量代替这层；本次核对书目信息 |
| 嗅叶增益 | Olsen等2010，Divisive normalization in olfactory population codes，DOI 10.1016/j.neuron.2010.04.009 | ORN→PN转换、网络归一化/增益调节 | 有效输入输出规律不等于每条LN受体/电导均已确定；本次核对书目信息 |
| 嗅叶时序 | Nagel等2015，Synaptic and circuit mechanisms promoting broadband transmission of olfactory stimulus dynamics，DOI 10.1038/nn.3895 | 快速气味变化如何经过突触和回路传递 | 若研究脉冲气味或时序学习应优先补读；本次核对书目信息 |
| PN→KC组织 | Caron等2013，Random convergence of olfactory inputs in the Drosophila mushroom body，DOI 10.1038/nature12063 | 组合汇聚与稀疏编码的经典依据 | 应结合后续结构偏好研究；本次核对书目信息 |
| PN→KC修正 | Zheng等2022，Structured sampling of olfactory input by the fly mushroom body，DOI 10.1016/j.cub.2022.06.031 | PN→KC采样中的结构偏好，检验完全随机假设 | 有真实连接组时优先用真实边，不重新随机覆盖；本次核对书目信息 |
| KC/APL功能 | Lin等2014，Sparse, decorrelated odor coding in the mushroom body enhances learned odor discrimination，DOI 10.1038/nn.3660 | APL反馈、KC稀疏度、气味区分 | 不能把单一稀疏率目标当作全部功能；本次核对书目信息 |
| APL局部性 | Amin等2020，Localized inhibition in the Drosophila mushroom body，DOI 10.7554/eLife.56954 | APL局部抑制、空间活动与反馈 | 不宜无条件视为全局均匀抑制；本次核对书目信息 |
| 蘑菇体连接 | Li等，The connectome of the adult Drosophila mushroom body provides insights into function，DOI 10.7554/eLife.62576 | KC/APL/MBON/DAN身份、分区、直接及跨分区网络 | hemibrain数据，不能与MaleCNS/FlyWire的原始ID直接混用；本次读全文资源与数据可用性部分 |
| 学习可塑性 | Hige等2015，Heterosynaptic Plasticity Underlies Aversive Olfactory Learning in Drosophila，DOI 10.1016/j.neuron.2015.11.003 | 多巴胺相关KC→MBON突触可塑性；特定实验条件下的学习规则 | 不能无条件推广为所有分区相同参数/规则；本次核对书目信息 |
| 持续反馈 | Zhao等2018，Persistent activity in a recurrent circuit underlies courtship memory in Drosophila，DOI 10.7554/eLife.31425 | M6→PAM-γ5反馈的功能和NMDA相关药理依据 | 雄蝇求偶背景，不可泛化所有MBON→PAM；上一轮已读公开全文Figure4及相关正文 |
| 长短期交互 | Huang等2024，Dopamine-mediated interactions between short- and long-term memory dynamics，DOI 10.1038/s41586-024-07819-w | γ1 MBON抑制反馈、PPL1-α3去抑制、训练间隔与再暴露效应、放电率拟合 | 厌恶学习特定通路/范式，不是全PAM/PPL1统一规则；上一轮已读公开全文 |
| 兴奋/抑制符号 | Liu/Wilson2013，Glutamate is an inhibitory neurotransmitter in the Drosophila olfactory system，DOI 10.1073/pnas.1220560110 | 果蝇GluCl相关抑制机制 | 不意味着全部谷氨酸连接为负；本次核对书目信息 |
| 脉冲传播代码基线 | Shiu等2024，A Drosophila computational brain model reveals sensorimotor processing，DOI 10.1038/s41586-024-07763-9 | 连接组LIF基线、激活/沉默接口、全网络脉冲输出 | 不是现成的完整嗅觉学习模型；本次核对全文代码/数据可用性、仓库README，未运行 |

## 已核对的数据和代码入口

- DoOR数据：https://github.com/ropensci/DoOR.data ；处理/查询函数：https://github.com/ropensci/DoOR.functions 。README给出安装方法及版本。两仓库分别是数据和R工具，不是可独立复现全部嗅觉行为的神经模型。
- Benton2025公开全文：https://europepmc.org/articles/PMC12187929 。补充材料列出Data Set EV1 (`44319_2025_476_MOESM2_ESM.xlsx`) 与EV2 (`44319_2025_476_MOESM3_ESM.zip`)。本次已核对附件存在，直接Springer CDN下载EV1返回HTTP错误，未取得或解析表格；不把列名或完整度当作本次已检查事实。用户之前上传的原论文及译稿可并用。
- neuPrint：https://neuprint.janelia.org/ ，Python客户端：https://github.com/flyconnectome/neuprint-python 。在线查询通常需要自行登录取得token；未使用/保存用户凭据。
- MaleCNS查询R包：https://github.com/natverse/malecns 。README提供类型/元数据、形态读取及`flywireType`/`mancType`等对应字段。它是数据访问工具，不是神经仿真器。官方数据项目：https://www.janelia.org/project-team/flyem/male-cns-connectome （来自该README，本次未另行验证该网页下载流程）。
- FlyWire形态/连接查询工具：https://github.com/navis-org/fafbseg-py 。形态、骨架、连接、注释和跨脑坐标变换；不是所有神经元身份都能无误一一匹配。
- Shiu原作者模型：https://github.com/philshiu/Drosophila_brain_model 。`model.py`、`example.ipynb`、`figures.ipynb`；原始仿真结果存档：https://doi.org/10.17617/3.CZODIW 。本次未下载大结果集、未跑模型。
- 蘑菇体连接论文的数据入口：https://europepmc.org/articles/PMC7909955 ，公开连接组集合DOI 10.25378/janelia.12818645.v1 （论文Data availability列出）。查询并锁定明确数据版本，不默认论文版本就是服务当前版本。

所有仓库在`repositories.json`中保存本次实际查询到的不可变commit。文献题目/DOI/PMC由Europe PMC检索；阅读深度按上表区分，不将摘要/元数据检索表述为全文精读。

## 对我们的模型最合适的落地顺序

1. 先限定成年、性别、脑侧、连接组版本以及气味的化学身份/浓度/给药时序。以一个连接组作结构主体；其他数据按细胞类型映射提供证据，不混用原始ID。
2. 用Benton的身份目录和DoOR/原始电生理构建气味→ORN通道对应。把未测响应、旧名称和不确定映射单独记录。动态输入需适应/转导模型或实测波形。
3. 提取ORN→PN/LN→KC/APL的真实网络，先在未学习条件下检验响应谱、浓度增益、时间波形及KC稀疏度。不要先人为把每种气味指定成互不相关的KC向量。
4. 接入分区化KC→MBON及DAN调制。先用特定分区实验标定，再引入MBON→DAN和跨分区反馈，检验具体激活/抑制/消融现象。
5. 结合用户HTML时先补成像细胞类别、空间位置、采样率、气味浓度和T6干预定义，再设spike→Ca→荧光观测层。不能逐ROI强行匹配未知身份的连接组细胞。
6. 若目标要解释先天趋避/学习后行为，再接PN→侧角、侧角/MBON汇合与下游行为读出；若只研究编码/学习，第一阶段可暂不模拟全VNC和肌肉。

神经动力学方面：Shiu代码可作可复现的LIF脉冲基线，但用户若要求详细生理模型，应按实测证据为关键ORN/PN/KC/APL或反馈DAN加入适应、电导型突触、受体动力学或多区室结构。不能靠统一HH参数取代标定。APL的非脉冲/局部机制尤其不应机械套用普通LIF。结构已知不代表电导、时间常数、受体、短时可塑性及多巴胺释放规律都已知。

## 最小优先阅读集

先读Benton2025总表、DoOR2.0、Olsen2010嗅叶归一化、Lin2014/Amin2020的APL、Li的蘑菇体连接、Hige2015学习、Huang2024反馈门控。需要可运行基线时读Shiu2024并检查原作者仓库；需要外周时间动态时补Nagel2011/2015。
