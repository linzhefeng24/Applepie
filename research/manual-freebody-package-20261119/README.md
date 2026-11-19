# 手调R2自由身体交付

用户要求将旧FixedBody视频替换为手调自由身体视频，并确认包内有参数。旧8.3MB包仅为结果补丁，缺失model.yaml。新包为独立完整交付，包含原手调神经模型、原生AB身体参数、神经代码、回放接口、状态、三份视频和现象审计。

`build.py`核验模型、原神经输入、原AB身体存档的SHA256再组装。`run_manual.py`在原生AB自由身体连续积分0.4秒，神经时钟倍率3，与此前Manual基线一致。已实际运行并匹配关节MSE0.1171784031；全程无固定根、无救援外力、无姿态重置，保留原11条辅助控制。原手调神经记录沿用已恢复计算结果并核验身份，物理仿真和视频为本轮新生成。

`input-identities.json`保存来源身份；`replay-verification.json`保存新积分证据；`replay.yaml`保存实验设置。完整包内说明见PACKAGE_README.md。此版本不采用任何BPTT权重，不将恢复AB肌肉输入替代神经控制，也不声称长期稳定行走。未重启已停止训练。

## 新版下载（替代旧固定身体补丁）

- [完整压缩包，含原手调参数、代码和三份自由身体视频](https://github.com/linzhefeng24/Applepie/releases/download/manual-r2-freebody-20261119/Manual_R2_FreeBody_Complete.zip)
- [自由身体视频](https://github.com/linzhefeng24/Applepie/releases/download/manual-r2-freebody-20261119/Manual_R2_FreeBody.mp4)
- [身体与神经链同步视频](https://github.com/linzhefeng24/Applepie/releases/download/manual-r2-freebody-20261119/Manual_R2_Synchronized.mp4)

约94MB，全部5个发布文件已重新下载校验大小与SHA256。旧FixedBody链接仍是历史固定版本，请使用本新版链接。最终ZIP逐文件清单排除自身哈希，避免自引用；新包解压后的独立物理回放已验证。
