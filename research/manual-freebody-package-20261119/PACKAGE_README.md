# 手调R2参数：自由身体视频与完整可运行文件

本包替代旧FixedBody结果补丁。默认视频不固定躯干，保留地面、摩擦、原生NoSlip/流体与原AB的11条头/腹/黏附等辅助通道。130条肌肉控制来自原手调R2神经网络输出，不采用BPTT第123/1000/281轮权重，也不直接播放AB肌肉目标轨迹。

01_model/model.yaml：原封不动的完整手调神经模型、连接、神经肌肉接口参数；SHA256为858d1818…；01_model/body_parameters.yaml：恢复成功AB的原生完整身体数值、资产、初态及辅助输入；replay.yaml：0.4秒回放协议，神经时钟3倍，与此前Manual对照一致。两个参数文件各有作用，不是两个候选神经模型。

02_code/run_manual.py：默认运行入口，持续积分自由身体、生成三份同步视频；flymodel/：原神经动力学和神经链显示接口；native_ab.py：原生身体计算。03_phenomena/：历史现象审计，沿用原报告，不代表本次全重新验证。04_results/data/：原手调神经记录、新物理状态、解码手调参数；04_results/videos/：身体肌肉、神经链3D示意、同步视频；report.json：检查结果。

## 运行

使用Python3.12，先 `python -m pip install -r requirements.txt`，再执行 `python 02_code/run_manual.py --render`。bash/bat入口调用同一脚本，均不含固定身体选项。Windows启动入口未在Windows实机测试；Linux EGL回放已验证。

默认复用包内原手调神经状态（哈希核验），重新积分身体并渲染。加 `--recompute-neural` 可从手调参数重新计算神经状态后回放。神经传播与中间状态API在flymodel.Model中。

## 已核对

完整model.yaml与BPTT之前手调锚点哈希一致，3988×细胞参数数组逐字节一致；手调全局参数、通道门控、突触与MN映射也保存在同一模型文件。另附解码的manual-resolved-parameters.npz便于查看；没有加载优化检查点。

视频为0.4秒物理回放的慢放，非1.4秒固定身体实验。此处明确使用后来恢复的原生AB环境和完整辅助输入，避免旧通用身体接口遗漏时变辅助输入。视频展示实际回放结果，不保证长期稳定行走。神经链图为分层示意，不是EM真实形态；绿表示中枢抑制/肌肉激活下降，不代表抑制性神经肌肉接头。
