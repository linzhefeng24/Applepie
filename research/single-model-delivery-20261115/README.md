# 单模型交付构建源

用户交付物是`dist/UnifiedFlyModel_20261115.zip`，内部只有一个模型文件和对应运行代码、现象JSON及视频。这里保存构建配方和输入身份，历史候选不进入ZIP。

`build.py`从已提交的3988细胞结构、R2解析参数、候选运动单位映射和原生130肌肉身体资产生成唯一`01_model/model.yaml`。大模型和最终压缩包以GitHub草稿Release保存，不直接塞入Git。

步骤：安装`runtime/requirements.txt`，运行`python build.py`；`verify_source.py`对照冻结神经运行；从生成目录执行`python 02_code/run.py demo`。随后执行打包脚本，校验清单必须包含两个单独视频和同步视频。所有参数出处和估计状态保存在模型文件；未确认项目在唯一phenomena.json中列出。
