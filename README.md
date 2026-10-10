# 慢慢的死亡笔记 · Ink Raven

## React + TypeScript 网页项目

围绕慢慢形象制作的纯前端日记本：死亡笔记封面、原作规则概述、可书写的笔记页。

- [网页源码与运行说明](web/)
- [下载独立源码包](downloads/manman-notebook-react-ts.zip)
- [封面预览](web/preview/cover-desktop.png) · [规则页预览](web/preview/rules-desktop.png) · [笔记页预览](web/preview/notebook-desktop.png)
- [浏览器功能验证记录](web/preview/validation.json)

支持多页笔记、自动保存、刷新恢复、文本导出和删除确认；适配电脑与手机。首页暂用静态图片，按 `web/README.md` 可接入背景视频。笔记仅保存在当前浏览器，不上传到服务器。

![网页封面预览](web/preview/cover-desktop.png)


原创卡通死神角色的第一版概念图。

## 当前版本：现代都市楼顶

现代日本城市夜景，铁丝围栏、空调外机、天线与雨后楼顶。保留角色形象，用冷色调和强烈明暗对比营造悬疑氛围，作为后续 5 秒视频的首帧。

![墨鸦现代都市场景](images/ink-raven-modern-city.png)


![墨鸦角色设定图](images/ink-raven.png)

## 角色特点

- 不对称墨圈眼与暗金色眼睛
- 一对笔尖角，其中一根断裂
- 外侧墨黑、内侧泛黄的书页翅膀
- 随身迷你笔记本，喜欢吃橡皮擦

## 查看与下载

打开 `images/ink-raven.png` 查看原图，并使用 GitHub 的下载按钮保存。

## 月夜屋顶场景

为后续 5 秒动态视频制作的横向场景图：月光、哥特建筑、薄雾与湿润屋顶。

![墨鸦月夜屋顶场景](images/ink-raven-moonlit-rooftop.png)

## 当前视频：转头、摇头与抬手动作版

- [下载 5 秒循环版](videos/ink-raven-performance-loop.mp4)
- [下载 Kling 原始生成版](videos/ink-raven-performance-original.mp4)
- [第二版逐秒动作提示词及参数](VIDEO_PROMPT_V2.md)
- [循环版验证结果](videos/ink-raven-performance-loop.validation.json)

Kling V3 生成后，循环版经过结尾过渡和时长校准。已验证：5.000 秒、1080p、24 fps、120 帧，解码后的首尾画面完全一致。原始模型输出为 5.041667 秒。

实际画面包含转头、抬手展示橡皮擦和羽翼随动；动作幅度和时机与逐秒提示词有一定差异。
