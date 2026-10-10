# 死亡笔记

纯前端 React + TypeScript 日记本，无后端、无 API Key。

## 双击打开（无需安装）

完整版 `downloads/death-note-react-ts.zip` 同时包含 `src/` 源码与 `offline/` 运行版。全部解压后，双击根目录 **打开笔记本.html**，这个简短入口会打开已生成的运行版，不需要安装或输入命令。

浏览器运行的是源码生成的 JavaScript，无法直接运行 TSX。修改 `src/` 后，开发者运行 `npm run export:offline` 更新运行版，入口文件无需修改。请保留 `offline/` 文件夹。

下载仓库 `downloads/death-note-offline.zip`，全部解压后双击 **打开笔记本.html**，使用 Chrome 或 Edge 即可。无需 Node.js、命令或网络，包含首页背景视频。请保留同目录的 assets 文件夹。

笔记存储与浏览器和本地文件位置有关，请固定文件位置、使用同一个浏览器，并导出重要笔记。

开发者可运行 `npm run export:offline` 重新生成 `offline/` 免安装版本。

## 本地运行

需要 Node.js 22.12+ 或 Node.js 24。

```bash
cd web
npm ci
npm run dev
```

## 三个页面

- `#cover`：死亡笔记封面，使用新制作的 5 秒连贯动作视频作为背景，静音自动循环播放。
- `#rules`：原作基础规则的中文概述，支持分类、搜索和注释。
- `#notebook`：一张无标题、无分区的横线书页，直接输入名字，自动保存；行间点缀淡色原创短句。

笔记只保存在当前浏览器的 localStorage 中，不会上传到服务器。清除站点数据会删除笔记，请导出重要内容。

## 首页背景视频

已内置 `public/assets/cover-background.mp4`，默认启用，无需环境变量。视频是连贯动作版本的网页压缩副本，保留 5 秒时长。切换到规则页或笔记页时停止播放，仅保留静态图片。

如需更换视频：

1. 将视频放到 `web/public/assets/cover-background.mp4`。
2. 将 `.env.example` 复制为 `.env.local`，设置：

```dotenv
VITE_HOME_VIDEO_URL=./assets/cover-background.mp4
```

3. 重新启动开发服务，或重新构建。

视频将静音自动播放并循环，播放失败时回退到现有静态图片。

## 检查与构建

```bash
npm run typecheck
npm run build
npm run preview
```

构建输出在 `dist/`。资源路径是相对路径，页面使用 hash 导航，可部署到静态站点的子目录。

## 技术栈

React 19、TypeScript、Vite、Lucide 图标、本地字体文件。字体和图片均随项目提供，页面不依赖远程字体服务。
