# 身体与环境驱动的感觉接口（新实现）

从旧A/B模型的每个实际物理步读取六腿胫节角度/速度、全部腿部地面接触力、足端接触力和切向力。接触力使用 MuJoCo contact frame 转到世界坐标，并按 geom1/geom2 正确取反。没有把关节力矩称作地面力，也没有把接触力称作外骨骼应变。

`body_sensory.sample_mechanics(model,data)` 可在每个身体步调用；`transduce()` 产生六腿 hook/claw、压缩负载及足端接触输入电流。接触与负载来自模拟环境，不是指定的周期。负载/触觉传递函数、位置中性角和增益是待标定近似，没有对应EM ID。

身体使用仓库已有 `research/assets/flymimic-legacy-AB-twofile.zip`，内含 simulation.py 和 parameters.yaml。解压到任意目录后：

```
/path/to/mujoco-3.3.2-python extract_body.py --model-directory /path/to/extracted --case A
```

保留141路旧控制。用克隆data计算观测所需forward，实际积分状态不被观测修改。模型原生质量单位未确证，因此保存原生力和同单位的体重倍数，不猜测µN。默认地面、无地面、1.5倍重力是不同环境干预。

该阶段是身体→感觉电流→感觉神经动力学接口；尚未把有解剖身份的感觉输出边接回VNC，更不等于端到端闭环行走。旧神经刺激实验仍单独保留。

## 最新手动候选与复跑

`parameters-position-r3.json` 将位置通道共享增益6→18pA/deg（250pA饱和），六腿各至少一条位置通道达到阈值。不宣称恢复已测的80°附近U形群体曲线。负载校准使用固定原模型体重，增加重力时不重新归一化感受器。

chief神经源最新候选在相邻研究目录 `configs/sensory-command-r6.json`：六个同型细胞兴奋增益1.5，已有DNg74→IN09A012电导增益3.5；均为未知生理参数假说，无连接增删。r4/r5失去部分抑制的结果保留。

```
/path/to/neural-python run_body_neurons.py A-ground --chief-mode motor --source-tag r6 --transduction-config parameters-position-r3.json --output-tag position-r3
/path/to/neural-python review_causal_phenomena.py
```

并列运行 passive、motor_web、motor_chief_off。身体A/B控制来自存档，chief指令试验独立运行，两者t=0对齐；只有200–400ms重叠指令期，不重排、不重复身体轨迹。这是双输入因果试验，不能宣称该DN网络生成了A/B运动。

力与姿态读取验证见 `results/observation-validation.json`；两套A/B最终qpos与不读取感觉的回放逐元素完全一致。已有脑回路r9的转向/停止实验未重新调参，本轮改变仅在独立MANC感觉子图和感觉接口，不能把它计作新的转向/停止通过结果。详见 `RESULTS.md`。
