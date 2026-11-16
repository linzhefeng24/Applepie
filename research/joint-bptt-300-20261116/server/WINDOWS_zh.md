# 在Windows电脑本地运行（WSL2，CPU）

计算发生在你的Windows电脑上。使用WSL2的Ubuntu24.04沿用已验证的Linux运行环境；不需要连接之前的服务器。
GitHub上的训练独立继续。当前这份程序固定CPU运行，不会因为电脑有显卡就自动使用GPU。
已验证的是Linux解压、模型加载及检查点恢复；尚未在你的Windows电脑上实测速度。

## 1. Windows PowerShell：安装Ubuntu24.04

以管理员身份打开Windows PowerShell，执行：

```powershell
wsl --install -d Ubuntu-24.04
```

按提示重启Windows，然后从开始菜单打开“Ubuntu24.04”，首次启动时自行创建一个本地Linux用户名和密码。
这不是之前服务器的账号，密码输入时不显示字符是正常现象。
已有WSL时可先用 `wsl -l -v` 查看；目标Ubuntu应使用WSL版本2。
请使用Ubuntu24.04，因为它默认是本程序所需的Python3.12。不要把后续Linux命令粘贴进PowerShell。

## 2. Ubuntu终端：安装、下载并检查

以下都在Ubuntu窗口内执行：

```bash
sudo apt-get update
sudo apt-get install -y python3-venv wget unzip
cd ~
wget -O Applepie_Server_JointBPTT.zip https://github.com/linzhefeng24/Applepie/releases/download/server-joint-bptt-20261116/Applepie_Server_JointBPTT.zip
unzip -q Applepie_Server_JointBPTT.zip -d applepie_local
cd ~/applepie_local
bash setup.sh
bash run.sh info
bash run.sh check
```

本包虽名为Server，也可直接在本机WSL运行。无须conda、GitHub登录或GitHub令牌。
请保持模型和运行目录位于Linux家目录 `~/applepie_local`，以免把大量运行文件放在 `/mnt/c/` 下拖慢磁盘访问。
若已存在同名目录，请改用新的解压目录，不覆盖已有实验。

`check`只加载完整模型、核验输入及恢复参数，不执行优化。`info`显示WSL可见的内存和CPU。
完整计算建议至少16GB可用内存，32GB物理内存电脑更宽裕；WSL默认通常只分配宿主机内存的一部分。
内存不足时不要同时运行多个训练进程。可先把 `info` 的输出发给我，确定分配方案。

## 3. Ubuntu终端：先测两轮

```bash
nohup bash run.sh benchmark > benchmark.log 2>&1 &
tail -f benchmark.log
```

首轮包含编译，第二轮用于与GitHub约502秒/次比较；不能预先保证本机更快。
首次完整更新可能需要十几分钟或更久，取决于本机硬件。
按Ctrl+C退出的是日志查看，后台任务仍运行。保持电脑开机且不休眠。
不要同时对同一run目录启动两个进程。

测速结束会显示 `Run directory` 和 `Export`，并在 `exports/` 生成结果ZIP。
将该ZIP发送给我即可核对速度与损失。

## 4. 查看文件、继续训练

在Ubuntu内执行以下命令可打开Windows资源管理器查看结果：

```bash
cd ~/applepie_local
explorer.exe .
```

从测速产生的参数继续运行，使用日志里的实际目录：

```bash
cd ~/applepie_local
nohup bash run.sh train --resume runs/实际测速目录 > train.log 2>&1 &
tail -f train.log
```

会完成剩余预试，然后从原手调基准进行正式300次更新。每次更新后保存在本机run目录。
重启电脑或关闭WSL服务会中断本机进程；重新进入Ubuntu后，用同一个 `--resume` 目录恢复。
正常关闭日志窗口不影响GitHub训练。结果不会自动覆盖GitHub那一路。

查看或导出当前结果：

```bash
bash run.sh status --run runs/实际运行目录
bash run.sh export --run runs/实际运行目录
```

完成300次后的可选视频生成命令及科学限制见本包的 `README_zh.md`。
