# 身体与环境驱动的感觉接口（新实现）

从旧A/B模型的每个实际物理步读取六腿胫节角度/速度、全部腿部地面接触力、足端接触力和切向力。接触力使用 MuJoCo contact frame 转到世界坐标，并按 geom1/geom2 正确取反。没有把关节力矩称作地面力，也没有把接触力称作外骨骼应变。

`body_sensory.sample_mechanics(model,data)` 可在每个身体步调用；`transduce()` 产生六腿 hook/claw、压缩负载及足端接触输入电流。接触与负载来自模拟环境，不是指定的周期。负载/触觉传递函数、位置中性角和增益是待标定近似，没有对应EM ID。

身体使用仓库已有 `research/assets/flymimic-legacy-AB-twofile.zip`，内含 simulation.py 和 parameters.yaml。解压到任意目录后：

```
/path/to/mujoco-3.3.2-python extract_body.py --model-directory /path/to/extracted --case A
```

保留141路旧控制。用克隆data计算观测所需forward，实际积分状态不被观测修改。模型原生质量单位未确证，因此保存原生力和同单位的体重倍数，不猜测µN。默认地面、无地面、1.5倍重力是不同环境干预。

该阶段是身体→感觉电流→感觉神经动力学接口；尚未把有解剖身份的感觉输出边接回VNC，更不等于端到端闭环行走。旧神经刺激实验仍单独保留。
