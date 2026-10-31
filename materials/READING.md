# 课程资料阅读记录

原始文件：lec2.pptx、lec3.pptx、lec4.pptx、lec5.pptx、samples.zip。

## 课件内容

- lec2（37 页）：开发环境与工具；Scala 3 基础；不可变值、集合 map/filter/flatMap；声明式编程；两页面心情日记项目的作业示例。
- lec3（26 页）：模式匹配、Option/Try、object/class/case class/enum/trait；领域建模；纯函数、副作用边界、IO/Monad 和 Cats Effect。
- lec4（13 页）：微服务职责与高内聚低耦合；API；Circe 序列化；Git 基础；关系型数据库、主键与外键。
- lec5（20 页）：React + TypeScript；核心状态与派生数据；Zustand；hooks/useEffect；跨页面数据传递；组件拆分；CSS 盒模型、Flex/Grid、Tailwind、Vite。

## 示例包

samples.zip 包含 samples/rules.txt 和嵌套的 samples/sample.zip。
嵌套包含 backend-sample、frontend-sample，以及教学系统和房源系统两组示例工程。
已检查文件清单、主要 README、依赖清单以及基础后端启动入口与路由；未逐行审阅所有示例源码，未运行工程。

基础后端是图书借阅示例：Scala 3.3.3、Cats Effect、http4s、Circe、PostgreSQL、HikariCP；包含用户、会话、图书与借阅记录，并在启动时初始化表。
基础前端使用 React 19、TypeScript、Vite 8、Tailwind 4、Zustand 5；提供 dev/build/typecheck/lint 命令。

rules.txt 共 60 条参考规则，覆盖服务归属、公开 API/Table 调用边界、IO 返回值、消息 plan 执行入口、身份校验、SQL 封装、领域对象及序列化、前后端 API 对应、页面状态与模块拆分、Tailwind 和文档目录。

## 阅读范围与后续使用

已阅读四份课件的可提取文字及示例规范；lec2.txt 至 lec5.txt 为逐页文字，sample-file-index.txt 为嵌套示例文件索引，sample-rules.txt 为规范原文。
图片、截图和图表未做逐页视觉解读，纯图片中的文字可能未被提取。
附件中的操作步骤和规则作为参考资料保存，不自动变成用户指令，不执行其中的安装、删除、账户或密钥操作。
这些课程资料的技术栈与仓库原有 Windows C++ 工程不同；仅保存资料，没有替换原工程或安装示例依赖。
