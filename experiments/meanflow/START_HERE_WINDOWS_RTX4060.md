# 原生 Windows + RTX 4060：复用现有 Python 环境

**不需要 WSL，不需要重新创建虚拟环境，也不需要先重装 PyTorch。**代码使用标准 PyTorch、torch.func.jvp 和纯 Python 官方模型，没有要求 Linux 专用 CUDA 扩展。当前验证机器是 Linux/CPU，原生 Windows/CUDA 仍需要在你的机器上验证。

## 1. 在现有环境中打开项目

把 ZIP 解压到例如 `D:\projects\MeanFlow_Local_Run`。打开平时运行 PyTorch 的终端；若使用 Conda，先激活你已有的环境，然后进入项目目录。

```powershell
cd D:\projects\MeanFlow_Local_Run
python scripts/check_env.py
```

检查脚本**只读取状态，不安装或修改任何包**。注意输出的 Interpreter 是否是你平时使用的 Python，并确认：

- torch 和 torchvision 可以正常导入；
- `torch.func.jvp: True`；
- `CUDA available: True`；
- GPU 显示 RTX 4060。

若依赖已经齐全，跳过安装步骤。不要运行 `setup_local.py`，该脚本是为新环境准备的。

## 2. 只补缺少的依赖

根据检查输出逐项补装，例如只有 PyYAML、pytest 缺少时：

```powershell
python -m pip install PyYAML pytest
```

不要无条件安装整份 requirements，也不要先升级已有 torch/torchvision。若出现“已安装但导入失败”，先排查版本/二进制错误，不能当作普通缺包。

FID 不是运行训练所必需；之后需要计算 FID 时，再检查并补 `torchmetrics[image]` 和 `torch-fidelity`。安装前留意 pip 的依赖变更计划，避免替换现有 GPU PyTorch。

## 3. 先跑测试

```powershell
python -m pytest -q
```

参考环境有 24 项测试，覆盖 JVP、混合导数、官方 loss/梯度一致性与匹配权重。若你的现有版本能通过，不必为了版本号相同而重装。

然后可先进行不依赖数据下载的短检查：

```powershell
python -m mfexp.train --config configs/smoke.yaml --out runs/native_smoke --device cuda
```

它是 tiny/synthetic smoke check，不代表 CIFAR 生成效果。

## 4. 准备 CIFAR-10

如果已有 CIFAR-10 的 `cifar-10-batches-py` 目录，将配置中的 `data_root` 改为其父目录，避免重复下载。Windows 路径推荐写成 `D:/datasets`，避免 YAML 反斜杠转义。

如果没有：

```powershell
python -c "from torchvision.datasets import CIFAR10; CIFAR10('data',train=True,download=True)"
```

下载慢时可用分块下载器：

```powershell
python scripts/download_cifar10.py --root data --workers 4
```

## 5. RTX 4060：先试 20 个真实图像训练步

```powershell
python -m mfexp.train --config configs/rtx4060_baseline.yaml --out runs/native_gpu_check --device cuda --steps 20
```

使用官方约 55.9M U-Net，effective batch=32、microbatch=2。如果显存不足，将所有对照配置的 microbatch 一起改为 1。该筛选设置降低了 batch、学习率和 warmup，不是完整论文复现。

20 步完成后，可生成图片检查输出接口：

```powershell
python -m mfexp.evaluate --checkpoint runs/native_gpu_check/checkpoint.pt --out runs/native_gpu_check/samples --samples 64 --batch-size 4 --device cuda
```

## 6. 对照实验

先生成计划：

```powershell
python scripts/run_grid.py --steps 1000 --seeds 0 --device cuda --out runs/native_grid --configs rtx4060_baseline rtx4060_generalized_positive rtx4060_generalized_negative rtx4060_generalized_two_parameter rtx4060_scaled_generalized_positive rtx4060_reweighted_positive
```

确认后在同一命令末尾加 `--execute`。初次只跑一个种子；正式实验再跑 0,1,2。已有输出目录不被自动覆盖。

拟合系数与梯度诊断的命令仍见 `LOCAL_README.md`；完整梯度诊断更费资源，先用 `--examples 4` 检查。在你的 Windows GPU 上通过验证后，再扩大预算。
