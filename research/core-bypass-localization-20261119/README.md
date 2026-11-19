# E2→I1 直接传递与 DNg100→MN 旁路定位

继续上一轮选中的 4159 细胞 I1 增益2候选；不覆盖原 R2，也不重启 BPTT。

输入模型 SHA256：`38b07321a54694dc875aebfaa82c930cd752bd0d25f2940ef7087fa45a44e4fa`。
来源：[上一轮完整候选](https://github.com/linzhefeng24/Applepie/releases/download/manual-core-extension-20261119/Selected_Core_Extension.zip)。

## 要检验的具体路径

1. E2 INXXX466 → I1 IN16B036：切直接边并保留其他全部连接，区分直接招募与间接网络作用。
2. DNg100 10056 → 左 promotor MN 800061/801173，分别29/26突触；DNg100 10045 → 右 promotor MN 802072，65突触。先切167条 DNg100→腿MN 边做因果对照，切边仅作诊断。
3. 保留真实连接，手动试该通路的未知终末效能0.5/0.25，及另一组共享MN兴奋性受体增益3/1.5（原为6），各做匹配E2沉默对照。这些均为未测量参数试探，不能当成真实生理值。

`initial_candidates.json` 来自上一轮已经核验的原始脉冲，1 ms 分箱只能筛候选，不能精确断言突触到达顺序。

本轮 `instrumented_dynamics.py` 仅在原内核追加每次脉冲的积分步与细胞索引日志，没有改方程或原运算顺序。baseline/E2_silenced 必须与上一轮对应条件的脉冲和u逐元素一致，才允许使用日志归因。默认条件从初态积分1600ms；最小回路持续验证为4000ms（cases.json显式覆盖），原步长0.0125ms，状态记录0.1ms。具体覆盖参数和干预定义均在 `cases.json`。

```bash
python setup_instrumentation.py
python experiment.py baseline cut_E2_I1 E2_silenced cut_DN_MN E2_silenced_cut_DN_MN
```

运行环境使用此前统一Python环境；当前目录内脚本默认使用仓库缓存的原R2代码及上一轮模型。`MANUAL_R2_PACKAGE` 可以指定原完整R2解压路径。

仍需区分：具体MN输出受某边影响、形成局部反馈、生成独立节律、复现实验消融表型，是不同层次的结论。本轮不通过简单压低总放电数或删除真实连接冒充成功。

首轮精确输入分解另发现：T1 I1 首次发放时，IN19B012（左800216、右801061）是最大单个兴奋性输入；两者又接受 E2 的358/287个突触。因此追加 E3→I1 单独切边、与 E2→I1 联合切边及 E3 沉默，区分直接与间接招募。相关候选及原始到达时刻见 `I1_indirect_candidates.json`；重建电导逐个样本与记录值核对，不能只按静态突触数量排序。


## 完成结果：29 个条件

- 原内核加日志后的 baseline/E2_silenced 与上一轮输出逐元素一致。29 个条件均通过有限状态、u边界和“精确事件重新分箱等于全部脉冲”检查，见 `verification.json`。
- 左前腿最小 DNg100(10056)+E1(800173)+E2(800863)+I1(801884) 回路：4秒积分中，DN持续约77.82Hz；1–3.9秒的E1/E2/I1单细胞间隔对应约13.4/13.4/13.5Hz。该数字是单次放电周期，不是包络频率。间隔有变化，不称为完美等周期。
- 沉默I1或切其返回E1/E2的边，E1/E2转为约39Hz；沉默E2，I1消失、E1约39Hz。由此支持最小反馈环的慢节律功能。最小条件的MN被钳制，未拿它证明肌肉活动。
- 完整网络I1输入汇合：切E2→I1后左右I1=0/7；切IN19B012→I1后=8/0；两路都切=0/0，基线为15/14。这是指定类型对在全网络的切边结果，不是仅切一条T1边。
- DNg100直接MN支路，以及INXXX464/其他DN旁路均由定向切边和输入电导分解定位。仅弱化直接DN支路或共同降低MN增益，未解决完整网络E2必要性，因此保留原选中候选。参数试探及选择理由见 `candidate_decision.json`。
- I1/I2单独及共同沉默均已测试；完整网络及DN+VNC中仍有替代输出，未将它判为文献冗余/消融现象复现。

图：`local-core-rhythm.png`、`I1-convergent-routes.png`、`MN-bypass-timelines.png`。逐神经元原始时刻和实际参数覆盖见 `results/*.json`，全分辨率状态与精确事件日志以Release压缩包保存；来源/哈希见 `manifest.json`。本轮没有修改原R2或上一轮主候选。

`phenomena_status.json` 明确区分最小模型成立、完整网络尚未成立，以及本轮未重测的实验现象。不存在新增“已完整复现实验行为”的计数。

## 在其他机器上重跑

先解压上一轮 `Selected_Core_Extension.zip`，记其目录为 `/path/to/selected`；当前诊断源码目录与该目录可分开放置：

```bash
export MANUAL_R2_PACKAGE=/path/to/selected
export CORE_MODEL_PATH=/path/to/selected/01_model/model.yaml
export CORE_REFERENCE_RESULTS=/path/to/selected/04_results
python experiment.py baseline cut_E2_I1 cut_E3_I1 cut_E2_E3_I1
python experiment.py T1L_core3 T1L_core3_I1_silenced T1L_core3_4s
```

依赖沿用上一轮 Python/numpy/numba/PyYAML，画图另外需要matplotlib。参考数据仅供baseline/E2_silenced的逐元素验证；积分始终从初态重新计算。其余输入和当前源码均在数据包内，模型及全部原始参数引用上一轮已经校验的发行资产，未重复存放。
