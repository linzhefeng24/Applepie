# E2→I1 直接传递与 DNg100→MN 旁路定位

继续上一轮选中的 4159 细胞 I1 增益2候选；不覆盖原 R2，也不重启 BPTT。

输入模型 SHA256：`38b07321a54694dc875aebfaa82c930cd752bd0d25f2940ef7087fa45a44e4fa`。
来源：[上一轮完整候选](https://github.com/linzhefeng24/Applepie/releases/download/manual-core-extension-20261119/Selected_Core_Extension.zip)。

## 要检验的具体路径

1. E2 INXXX466 → I1 IN16B036：切直接边并保留其他全部连接，区分直接招募与间接网络作用。
2. DNg100 10056 → 左 promotor MN 800061/801173，分别29/26突触；DNg100 10045 → 右 promotor MN 802072，65突触。先切167条 DNg100→腿MN 边做因果对照，切边仅作诊断。
3. 保留真实连接，手动试该通路的未知终末效能0.5/0.25，及另一组共享MN兴奋性受体增益3/1.5（原为6），各做匹配E2沉默对照。这些均为未测量参数试探，不能当成真实生理值。

`initial_candidates.json` 来自上一轮已经核验的原始脉冲，1 ms 分箱只能筛候选，不能精确断言突触到达顺序。

本轮 `instrumented_dynamics.py` 仅在原内核追加每次脉冲的积分步与细胞索引日志，没有改方程或原运算顺序。baseline/E2_silenced 必须与上一轮对应条件的脉冲和u逐元素一致，才允许使用日志归因。所有条件从初态积分1600ms，原步长0.0125ms，状态记录0.1ms。具体覆盖参数和干预定义均在 `cases.json`。

```bash
python setup_instrumentation.py
python experiment.py baseline cut_E2_I1 E2_silenced cut_DN_MN E2_silenced_cut_DN_MN
```

运行环境使用此前统一Python环境；当前目录内脚本默认使用仓库缓存的原R2代码及上一轮模型。`MANUAL_R2_PACKAGE` 可以指定原完整R2解压路径。

仍需区分：具体MN输出受某边影响、形成局部反馈、生成独立节律、复现实验消融表型，是不同层次的结论。本轮不通过简单压低总放电数或删除真实连接冒充成功。
