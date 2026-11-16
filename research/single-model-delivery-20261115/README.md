# 单模型交付构建源

用户交付物是`dist/UnifiedFlyModel_20261115.zip`，内部只有一个模型文件和对应运行代码、现象JSON及视频。这里保存构建配方和输入身份，历史候选不进入ZIP。

`build.py`从已提交的3988细胞结构、R2解析参数、候选运动单位映射和原生130肌肉身体资产生成唯一`01_model/model.yaml`。大模型和最终压缩包以GitHub草稿Release保存，不直接塞入Git。

步骤：安装`runtime/requirements.txt`，运行`python build.py`；`verify_source.py`对照冻结神经运行；从生成目录执行`python 02_code/run.py demo`。随后执行打包脚本，校验清单必须包含两个单独视频和同步视频。所有参数出处和估计状态保存在模型文件；未确认项目在唯一phenomena.json中列出。

`python finalize.py`解码检查全部视频、校验状态和唯一模型身份，再生成ZIP及SHA清单。`verify_distribution.py <zip> --report <json>`从全新临时目录解压，核对每个文件并测试公开状态、肌肉驱动和接触接口。

GitHub独立重跑工作流：`.github/workflows/build-single-model-delivery.yml`。最终附件保存在`unified-fly-model-20261115`草稿Release；不发布云环境或公开Release。`delivery-manifest.json`记录最终附件的实际URL、字节数、SHA及代码版本（重跑完成后写入）。本地早期打包与GitHub独立重跑分别记录，不将两者的ZIP哈希混用。

## Native AB comparison protocol

The originally delivered neural demo inherits A pose but intentionally zeroes velocity/activation and neutralizes auxiliary controls. It does not reproduce native AB conditions. For archived AB or checkpoint-to-AB body comparisons, use [the restored canonical replay](../restore-native-AB-20261116/README.md): complete initial state/warmstart, all11 auxiliary controls, native0.4s physics, and the declared neural-output clock map. Existing baseline hashes/checkpoints remain immutable.
