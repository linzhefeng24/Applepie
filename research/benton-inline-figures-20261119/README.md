# Benton 中文图文对应版

沿用 `../chinese-translations-20261118/translated.json` 的完整译文，将主图1–6及扩展图EV1、EV2插入对应中文图注之前，而非集中放在文末。图内标识和参考文献保留原文。非官方译稿，原文CC BY 4.0。

`render.py` 读取原始用户PDF，核对SHA256，按 `FIGURES` 的原页坐标渲染整张图（包含矢量标记），生成PDF、Word、独立HTML及ZIP。`layout-audit.json` 保存8张图的原页、裁剪范围、译文锚点和图像哈希。未改写译文及其他论文。

复现：`python research/benton-inline-figures-20261119/render.py /path/to/'Benton EMBO Reports 2025.pdf'`，需要PyMuPDF、python-docx。生成文件位于忽略的 `cache/delivery/`；Release发布清单位于 `manifest.json`。

已检查PDF含8张图、全部46段译文及正确图序，并目视检查中文、图注和图的布局。数据源/版本/裁剪位置见审计文件。发布使用原有SHA256校验的Git blob传输和官方GitHub Actions；不把大型文件提交至Git历史。

下载：
- [PDF](https://github.com/linzhefeng24/Applepie/releases/download/benton-illustrated-zh-20261119/Benton_2025_Chinese_Illustrated.pdf)
- [Word](https://github.com/linzhefeng24/Applepie/releases/download/benton-illustrated-zh-20261119/Benton_2025_Chinese_Illustrated.docx)
- [完整压缩包](https://github.com/linzhefeng24/Applepie/releases/download/benton-illustrated-zh-20261119/Benton_2025_Chinese_Illustrated.zip)
