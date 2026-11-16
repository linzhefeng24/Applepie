# 服务器运行包：完整神经—肌肉—物理联合 BPTT

本包用于与 GitHub 正在运行的版本对比速度，也可在服务器独立接着训练。
不需要 GitHub 登录、token 或服务器密码。它不会修改或停止 GitHub 训练。

## 包内有什么

- `research/joint-bptt-300-20261116/`：全3988细胞、485045条连接的 HH 神经动力学、MN→130肌肉接口、原生MuJoCo正向、白盒物理反向、正则项和Adam训练代码、梯度校验及失败记录。
- `research/single-model-delivery-20261115/build/UnifiedFlyModel/01_model/model.yaml`：唯一的手调基准模型，含神经连接、参数、候选MN肌肉映射。
- `research/assets/flymimic-legacy-AB-twofile.zip`：原始AB物理模型、完整初态、肌肉参数、地面接触和11路辅助控制。
- `checkpoint/optimizer.zip`：打包时已确认的检查点，含训练参数、Adam状态、历史和计数。具体阶段在 `checkpoint/origin.json`，不是永远保持最新。
- 原始R2手调参数、构建模型所需源数据、上游物理源代码和许可证也已包含。
- `PACKAGE_MANIFEST.json`：全部输入和代码的SHA256、训练源版本、打包版本及已知限制。

仅为脱离git目录运行，打包的训练入口有一行兼容性改动：设置源版本后不再额外调用git。数学、参数初值、优化器和正则项均未改；原文件和打包文件哈希都在清单中。
校验所需的历史脉冲数组由已验证稀疏事件重建，仅包含脉冲计数，不声称恢复历史膜电位。

## 1. 下载并解压（在服务器终端执行）

```bash
cd ~
wget -O Applepie_Server_JointBPTT.zip https://github.com/linzhefeng24/Applepie/releases/download/server-joint-bptt-20261116/Applepie_Server_JointBPTT.zip
unzip -q Applepie_Server_JointBPTT.zip -d applepie_server
cd ~/applepie_server
```

如果服务器不能访问GitHub，可在Windows浏览器下载后，在**Windows PowerShell**执行：

```powershell
scp "$HOME\Downloads\Applepie_Server_JointBPTT.zip" lzf@166.111.72.113:~/
```

然后回服务器执行上面的解压、进入目录命令。使用一个新目录，不覆盖旧模型或旧实验。

## 2. 准备Python3.12并安装

如果已有conda：

```bash
conda create -n applepie-joint python=3.12 -y
conda activate applepie-joint
bash setup.sh
```

如果没有conda，可以先安装到自己的用户目录（Linux x86_64）：

```bash
wget -O ~/Miniforge3.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash ~/Miniforge3.sh -b -p ~/miniforge3
source ~/miniforge3/etc/profile.d/conda.sh
conda create -n applepie-joint python=3.12 -y
conda activate applepie-joint
bash setup.sh
```

已有Python3.12也可直接 `PYTHON=/实际路径/python3.12 bash setup.sh`。
setup会建立独立`.venv`、安装固定版本并补齐MJX兼容代码，不修改系统Python。
建议至少16GB可用内存，32GB更宽裕。安装依赖时需要联网；安装完成后的训练不需要联网。

## 3. 检查机器和完整性

```bash
bash run.sh info
bash run.sh check
```

`info`显示CPU、内存、JAX设备和可用GPU。**当前可比版本固定CPU运行，显示有GPU不代表启用了GPU。**
`check`验证所有哈希、加载完整模型并恢复检查点，但不执行参数更新。成功后生成 `runs/...-check-.../server-result.json`。

## 4. 做两次完整更新测速

```bash
nohup bash run.sh benchmark > benchmark.log 2>&1 &
tail -f benchmark.log
```

这会新建独立的 `runs/...-benchmark-.../`，从打包检查点做两次真正的全神经网络→0.4秒物理仿真→反向→Adam更新。
首轮包含编译，以第二轮的 `seconds` 与GitHub约502秒/轮比较。测速可能需要十几至几十分钟；计算过程中长时间没有新日志不一定是卡住。
`Ctrl+C`退出的是 `tail`，后台测速仍继续。不要同时对同一个run目录启动两个训练进程。

完成后查看：

```bash
cat runs/实际测速目录/server-result.json
```

看 `per_update_seconds` 和 `last_update_speedup_vs_github_502s`。大于1表示服务器单次更新更快。
报告也包含总墙钟时间；预试末尾的额外评估和保存不计入每次更新的 `seconds`，但计入总时间。
不同CPU的浮点运算顺序可能影响硬脉冲，不能假定轨迹逐位相同。

## 5. 在服务器接着训练

若测速完成后希望从测速产生的参数接着跑：

```bash
nohup bash run.sh train --resume runs/实际测速目录 > train.log 2>&1 &
tail -f train.log
```

若希望从打包检查点单独开始：

```bash
nohup bash run.sh train > train.log 2>&1 &
```

训练入口保留已完成的预试、参数、Adam状态和正式计数，完成剩余系数比较后从手调基准开始正式300次更新，达到300便结束。预试不冒充正式训练。
每次更新后，本地 `research/joint-bptt-300-20261116/cache/train/` 保存完整状态；出错也保留最近成功的检查点。
断开SSH后nohup会继续运行。重新连接后，不需要再次安装，进入目录后使用 `--resume` 指定原run目录即可恢复。

## 6. 看进度、导出结果给我

```bash
bash run.sh status --run runs/实际训练目录
bash run.sh export --run runs/实际训练目录
```

导出的 `exports/目录名.zip` 包含检查点、历史、参数、环境信息、日志和输入清单，不包含账户或凭据。结束或报错时也会自动导出。
把该ZIP发给我，即可核对速度、损失和参数，并安排后续结果合并。服务器运行不会自动上传到官方训练Release，避免两台机器互相覆盖；GitHub那一路保持独立运行。

## 7. 完成300次后生成对比视频（可选）

视频代码已包含。Linux需安装EGL相关库；若有sudo权限：

```bash
sudo apt-get update
sudo apt-get install -y libegl1 libgl1-mesa-dri libgl1
```

回到解压目录执行（替换实际训练目录）：

```bash
package_root="$PWD"
cd runs/实际训练目录
MUJOCO_GL=egl "$package_root/.venv/bin/python" research/joint-bptt-300-20261116/finalize.py --local
```

结果在该run的 `research/joint-bptt-300-20261116/cache/final/`，包含原AB输入、手调版、最佳版、第300次版本的同场景对比视频和状态数据。
`--local`仅本地输出，不登录或上传GitHub。未完成300次时该入口会拒绝生成“300次结果”。

## 已知科学限制

正向是原版自由身体AB物理模型，保留地面、接触、NoSlip、流体阻力和辅助控制；不是固定身体，也没有救援力。
物理反向为近似解析/隐式梯度，20ms随机方向严格校验最大相对误差约13.3%，但负梯度方向的原生仿真下降测试通过；不声称已验证全400ms精确梯度。
神经侧使用代理梯度和200ms截断反向。26个MN→肌肉映射缺口仍为零输入，没有任意补齐。
服务器快不快需实测，尚未声称在你的服务器成功运行。
