# 已解压包在Ubuntu26.04因Python3.14停止：恢复步骤

观察到的错误是 `Please use Python3.12`，随后 `.venv/bin/python` 不存在。
运行包要求Python3.12；Ubuntu26.04默认Python3.14，版本检查发生在创建虚拟环境之前。
ZIP已下载、解压成功，可以沿用原目录。Docker软件源签名错误需另行处理，但本次包安装失败的直接原因是Python版本不符；本程序不依赖Docker。

以下在现有 **Ubuntu/WSL终端** 执行，不在Windows PowerShell执行。
使用uv提供的独立Python3.12，不替换系统Python，也不需要重装WSL。

## 自动处理版本（推荐）

```bash
cd ~/applepie_local
wget -O setup_auto.sh https://raw.githubusercontent.com/linzhefeng24/Applepie/main/research/joint-bptt-300-20261116/server/setup_auto.sh
bash setup_auto.sh
```

脚本自动寻找Python3.12；没有时自动准备uv及项目专用Python3.12，然后调用原始setup。
现有系统Python3.14保留，不需要手工选择解释器。自动脚本是新增文件，不覆盖原包已校验的setup.sh、模型或训练文件。
当前固定依赖jaxlib0.5.3的公开安装包只有cp310～cp313，没有cp314；这不是删除一个版本检查就能解决的。

## 手动处理（自动脚本无法下载时）

```bash
cd ~/applepie_local

# 下载官方uv安装器，安装到用户目录。
wget -O /tmp/applepie-install-uv.sh https://astral.sh/uv/install.sh
UV_INSTALL_DIR="$HOME/.local/bin" UV_NO_MODIFY_PATH=1 sh /tmp/applepie-install-uv.sh

# 下载并确认独立Python3.12。
"$HOME/.local/bin/uv" python install 3.12
python312_path="$("$HOME/.local/bin/uv" python find --managed-python 3.12)"
"$python312_path" --version

# 指定这个Python重新建立项目环境。
PYTHON="$python312_path" bash setup.sh
```

最后一条成功后再执行：

```bash
bash run.sh info
bash run.sh check
```

检查成功后开始两次更新测速：

```bash
nohup bash run.sh benchmark > benchmark.log 2>&1 &
tail -f benchmark.log
```

任一步报错就先停在该步，保留报错文本；不要在setup失败后继续运行benchmark。
本说明是根据用户粘贴日志诊断后新写的恢复步骤，没有声称已在用户Windows电脑执行成功。
原始终端日志包含临时签名下载URL等无关信息，不上传原始日志；仅保留通用错误与恢复方法。
