# 唯一模型：DN → VNC → MN → 六腿肌肉

本包只有一套模型与参数：**MaleCNS 3988细胞 / R2共享参数 + 旧130肌肉身体模型**。没有候选版本、历史实验目录或旧A/B控制轨迹。可直接观看`04_results/videos/`里的视频；安装依赖后可从头计算。

## 文件结构

```
01_model/
  model.yaml                 唯一数值模型：连接、细胞、肌肉、骨架、接触、初态、刺激和显示参数
  provenance.json            输入来源、SHA、版本及映射覆盖；不是第二套参数
02_code/
  run.py                     命令行入口
  example_api.py             多种输入/状态查询接口示例
  EQUATIONS.md               方程、单位和假设
  flymodel/dynamics.py        双区室HH/Ca/SK与电导突触；读取参数，不藏生理默认值
  flymodel/simulator.py       模型读取、DN输入、任意神经元状态、MN→肌肉、原生身体积分
  flymodel/render.py          身体及对应神经链3D视频
03_phenomena/
  phenomena.json             能做到、部分做到、不能做到/尚未检验；证据与范围
04_results/
  videos/01_body_muscles.mp4
  videos/02_neural_chain_3d.mp4
  videos/03_synchronized.mp4  上述两视频同步并排
  data/                      本次神经及身体状态，可读取任意已记录细胞/肌肉
  verification.json          实际运行身份、版本、运动及数值检查
requirements.txt
run_demo.bat / run_demo.sh
```

## 运行

需要64位Python3.12。已验证的运行平台在`04_results/verification.json`中；Windows启动脚本同时提供，Windows本身未在该Linux环境实测。

Windows可双击`run_demo.bat`（需要`py -3.12`）。Linux执行`bash run_demo.sh`。脚本只在本目录创建`.venv`并安装依赖，不修改系统Python。

手动方式：

```
python -m pip install -r requirements.txt
python 02_code/run.py inspect --type DNg100
python 02_code/run.py demo --experiment DN_drive
```

固定身体实验可执行 `python 02_code/run.py demo --experiment DN_drive --fixed-body`。
该模式移除身体根自由关节，将躯干固定在初始位置与姿态；腿关节及肌肉仍自由运动，地面碰撞、摩擦和接触力继续求解。固定支撑承担躯干反力，因此该模式不验证自由行走或平衡。

`demo`从DN输入重新运行神经、肌肉及身体，再生成三段同步视频。默认记录所有细胞，首次Numba编译需要一些时间。输入协议及数值均在`model.yaml/experiments`。可选`BRK`、`MDN`、`MDN_BRK`、`PFL3_left`、`BPN_FG`、`quiet`，使用同一模型参数。

只运行神经、读取中间状态、重渲染：

```
python 02_code/run.py neural --experiment BRK
python 02_code/run.py state --neural 04_results/data/neural_state.npz --type DNg100 --time-ms 500
python 02_code/run.py render
```

读取某个神经元的参数和连接：

```
python 02_code/run.py inspect --id <MaleCNS_ID>
python 02_code/run.py connections --id <MaleCNS_ID> --direction incoming
```

API见`02_code/example_api.py`：支持命名协议、自定义事件列表、全网电流数组、细胞消融、指定记录细胞、任意记录时刻的电压/Ca/m-h-n/电流/电导，以及独立肌肉输入、身体状态和接触力读取。默认神经积分步长与状态记录间隔不同；查询返回最近的实际记录时刻，精细记录可通过API指定。

## 参数与来源怎么读

`model.yaml`里的`parameter_provenance`逐类标明：

- **published_dataset**：原始连接方向和突触计数，保留MaleCNS版本及来源。
- **prediction_and_assumption / prior**：递质预测、Glu在CNS中的抑制符号、未实测通道与突触动力学。
- **mixed_prior_calibration_manual / manually_tuned**：成年MN参考校准、按相似类型共享的手调参数、R2末端效力。
- **estimated_mapping**：MN池到模型肌肉的功能类别对应；不是已确认的逐运动单位连线。
- **inherited_reconstruction**：原身体模型；每块肌肉还保留几何来源和估计状态。

神经元有17列显式已解析参数，列名、单位、类别/家族手调字段均在同一文件。大数组和网格为带SHA的base64数据，可用Python读取；不是外部隐藏模型。结构矩阵保存原始计数，效力乘数单独列出。没有重复的另一套有效模型。

身体的**骨架、关节位置/轴、惯性、接触、肌肉附着与动力学参数**统一在`body/mjcf`。这是唯一权威身体数值定义；肌肉目录只保留来源及索引，不再放另一套可能不一致的数值。

## 视频颜色与范围

身体视频是真实MuJoCo积分及肌肉路径显示，地面、重力和接触均启用，不施加救援力，不做运动中状态重置。初姿态继承旧A，初速度与激活置零；**没有播放旧A/B控制曲线**。神经先预运行到模型指定的时刻，之后身体开始一次连续积分，视频同时标出神经/身体时间。

神经链视频是**3D示意布局，不是真实EM神经元形态**；仿真计算全部有效连接，显示边为注明的抽样。神经元颜色表示净突触+外加电流，大小表示放电；红/绿边分别表示模型中的兴奋/抑制输出。肌肉红色表示激活，绿色表示激活下降，**不表示肌肉存在抑制性谷氨酸NMJ**。

## 重要边界

这是可运行的单向完整计算链，**不是已完备的真实连接组，也没有感觉→VNC闭环**。候选MN到肌肉映射含估计，缺失项请求输入为零；MuJoCo仍执行原生肌肉最小控制限。原130肌肉模型含估计附着、走线与强度，不能称为FlyMimic原版完整六腿解剖。

视频会保留真实身体表现，不能将有运动/有肌肉激活当作稳定行走或BRK制动成功。详见`03_phenomena/phenomena.json`。旧MANC局部节律模型的通过结果不会继承到本唯一MaleCNS模型。
