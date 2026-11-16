# 16GB Windows电脑的本地测速建议

依据用户报告：Windows物理内存约15.4GiB，WSL当前约7.5GiB，项目环境及模型加载检查已通过。
尚未在该电脑完成完整联合BPTT更新，下面是待用户应用的配置建议，不是已验证的性能结果。

先尝试WSL内存上限10GB、磁盘交换空间8GB，保留约5GB物理内存给Windows。
实际Windows可用容量还受应用占用影响；交换空间不是额外物理内存，大量交换可能显著降低速度。
先做两次更新测速，再决定是否本机长训。GitHub训练继续独立运行。

## Windows PowerShell：编辑配置

```powershell
notepad "$env:USERPROFILE\.wslconfig"
```

新文件可填：

```ini
[wsl2]
memory=10GB
swap=8GB
```

如果文件已有内容，保留其它配置，只在已有的 `[wsl2]` 节下修改或补充这两项，不要重复创建该节。
保存。确认WSL内没有需要继续运行的任务后，在PowerShell执行：

```powershell
wsl --shutdown
wsl
```

`wsl --shutdown` 会终止本机全部WSL发行版中的运行进程；不会停止GitHub上的训练。

## Ubuntu终端：核对并测速

```bash
free -h
cd ~/applepie_local
nohup bash run.sh benchmark > benchmark.log 2>&1 &
tail -f benchmark.log
```

核对WSL可见内存已接近10GB，交换空间接近8GB。不要同时启动多个本地训练。
首轮包含编译，第二轮更新耗时才适合与GitHub约502秒/次的参考值比较；是否更快需要实测。
如果出现 `Killed`、内存不足或长时间持续大量交换，应保留日志再检查，不要仅反复重启同一计算。
测速结束可通过Ubuntu的 `explorer.exe .` 打开项目目录，把exports中的结果ZIP交回核对。
