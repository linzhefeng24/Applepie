# Windows + WSL2 + RTX 4060：从这里开始

推荐在 WSL2 的 Linux 文件系统中运行，使用 Windows NVIDIA 驱动提供的 WSL CUDA 支持。4060 型号和可用显存以 `nvidia-smi` 显示为准；本配置没有在你的显卡上实测。

## 1. 将文件解压到 WSL

下载 ZIP 后，在 WSL 中解压到例如 `~/projects/MeanFlow_Local_Run`，进入目录。建议避免直接在 `/mnt/c` 上执行大量数据读取。

```bash
cd ~/projects/MeanFlow_Local_Run
nvidia-smi
python3 --version
```

推荐 Python 3.12，代码支持 3.10–3.12。若 WSL 中 `nvidia-smi` 无法识别 GPU，应先在 Windows 更新支持 WSL2 的 NVIDIA 驱动并确认 WSL2 正常；不要为此在 WSL 中覆盖安装 Linux 内核显卡驱动。无需仅为 PyTorch wheel 再安装完整 CUDA Toolkit。

## 2. 安装 CUDA 版依赖

```bash
python3 scripts/setup_local.py --backend cu126
source .venv/bin/activate
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

应显示 `True` 和 RTX 4060。若驱动不支持所选 CUDA wheel，先更新 Windows NVIDIA 驱动或根据 PyTorch 官方兼容关系选择版本。

## 3. 验证程序并下载数据

```bash
python -m pytest -q
python -c "from torchvision.datasets import CIFAR10; CIFAR10('data',train=True,download=True)"
```

标准下载慢时：

```bash
python scripts/download_cifar10.py --root data --workers 4
```

## 4. 先做 20 步 GPU 检查

```bash
python -m mfexp.train --config configs/rtx4060_baseline.yaml --out runs/gpu_check --device cuda --steps 20
```

筛选配置使用官方约 55.9M 参数 U-Net，有效 batch=32、microbatch=2、lr=1e-4、100 步 warmup。若显存不足，将所有对照配置的 `microbatch_size` 同样改为 1；有效 batch 不变。若仍不足，应先排查 GPU 占用，不要用不同模型规模直接比较各组。

## 5. 同预算运行对照

```bash
python scripts/run_grid.py --steps 1000 --seeds 0 --device cuda --out runs/4060_grid --configs rtx4060_baseline rtx4060_generalized_positive rtx4060_generalized_negative rtx4060_generalized_two_parameter rtx4060_scaled_generalized_positive rtx4060_reweighted_positive
```

上面只生成计划。确认后在同一命令末尾加 `--execute`，才会依次训练。

第一次只跑种子 0 检查流程；正式比较再用 `--seeds 0,1,2`。不要把 1000 步筛选当成收敛结果。筛选配置刻意降低 batch、学习率和 warmup，**不是论文的 800K 步原始设置**；所有组一起修改，才是公平的本地比较。

单卡 4060 上完整论文预算成本很高，本次没有估计或承诺训练完成时间。可先根据前 20 步的 JSON 日志中 `seconds` 估计本机速度。

## 6. 生成少量图片

```bash
python -m mfexp.evaluate --checkpoint runs/gpu_check/checkpoint.pt --out runs/gpu_check/samples --samples 64 --batch-size 8 --device cuda
```

20 步的图片没有质量意义，只验证采样。训练不足 16 步时 EMA 尚未更新，需要 `--raw`。FID-50K 会另外下载 Inception 权重并消耗时间，待模型充分训练后再测。

详细的梯度拟合命令见 `LOCAL_README.md`。大 U-Net 的完整梯度诊断比普通训练更费显存；先 `--examples 4` 检查，不能把 4 个样本的拟合当作可信研究结论。
