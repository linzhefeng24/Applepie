# 慢慢的死亡笔记

纯前端 React + TypeScript 日记本，无后端、无 API Key。

## 本地运行

需要 Node.js 22.12+ 或 Node.js 24。

```bash
cd web
npm ci
npm run dev
```

## 三个页面

- `#cover`：死亡笔记封面，使用慢慢的现代都市图片作为背景。
- `#rules`：原作基础规则的中文概述，支持分类、搜索和注释。
- `#notebook`：输入标题和正文，新建多页、切换、自动保存、导出文本及确认删除。

笔记只保存在当前浏览器的 localStorage 中，不会上传到服务器。清除站点数据会删除笔记，请导出重要内容。

## 之后接入首页背景视频

1. 将视频放到 `web/public/assets/cover-background.mp4`。
2. 将 `.env.example` 复制为 `.env.local`，设置：

```dotenv
VITE_HOME_VIDEO_URL=./assets/cover-background.mp4
```

3. 重新启动开发服务，或重新构建。

视频将静音自动播放并循环，播放失败时回退到现有静态图片。当前版本不启用视频。

## 检查与构建

```bash
npm run typecheck
npm run build
npm run preview
```

构建输出在 `dist/`。资源路径是相对路径，页面使用 hash 导航，可部署到静态站点的子目录。

## 技术栈

React 19、TypeScript、Vite、Lucide 图标、本地字体文件。字体和图片均随项目提供，页面不依赖远程字体服务。
