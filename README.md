# APERTURE · 金融研究终端

基于用户真实美股分钟行情的课程软件：检索与自选 → 个股年度指标与比较 → 五模型量化分析 → 滚动样本外回测 → 保存、导出研究报告。

## 已实现

- **研究概览**：32 个已导入标的、代码/名称检索、行业筛选、自选持久化、最近源价格与成交量。
- **个股研究**：历史价格、双股票共同日期归一比较、收益分布、2022–2026 年行情指标、数据质量。指标包括收益、波动、最大回撤、Sharpe、偏度、超额峰度。
- **量化实验室**：等权、最小方差、均值—方差、MVSK、风险平价；2–10 个标的、权重上限、高阶矩偏好、多起点优化与收敛状态、相关性热力图、权重与分布。
- **回测**：固定滚动估计窗口、滞后一整个收盘的信号、漂移持仓、交易费、同口径基准、净值与回撤、调仓审计、CSV 导出。
- **研究档案**：PostgreSQL 保存完整参数和结果；浏览、删除、Markdown / JSON 导出和浏览器打印为 PDF。
- 清楚区分加载、错误、空数据、计算中、就绪、求解失败回退；支持手机布局。

[下载 APERTURE.zip](https://github.com/linzhefeng24/Applepie/raw/refs/heads/main/downloads/APERTURE.zip)（不包含原 C++ 工程和课件）。

## 一个命令启动

只需要下载本项目目录，进入该目录的终端运行：

```bash
bash run.sh
```

也可以在任意目录指定脚本位置执行，例如 `bash "/你自己的目录/financial-terminal/run.sh"`。脚本自动定位项目，不要求目录必须叫 financial-terminal 或放在固定位置。

第一次会自动安装项目依赖、初始化本地数据库、构建前后端并启动全部服务。以后运行同一命令会复用已安装依赖；依赖清单、项目位置或源码变化时会重新安装或构建。启动成功后打印浏览器访问地址，默认端口 4173。无需自己分别启动数据库和多个微服务。

```bash
bash run.sh stop       # 停止本项目应用及项目管理的数据库，保留数据
bash run.sh restart    # 重启
bash run.sh setup      # 强制刷新依赖、重新构建并启动
bash run.sh help       # 查看说明
```

服务在后台运行，关闭当前终端后仍继续运行。日志位于 `.run/`，安装失败会显示原因，不会误报启动成功。自选和报告保存在本地 PostgreSQL 中；重复启动不清空这些记录。

### 自动准备基础环境

在 Ubuntu 22.04/24.04（包括 Windows WSL）和 Debian 13 中，直接运行 `bash run.sh`。缺少基础工具时会自动处理：

- Java 21 和 PostgreSQL：从发行版官方软件源安装，保留包签名验证。
- Node：版本不足 24 时，从 Node 官方下载并校验 SHA256，安装到项目 `.tools/runtimes/`，不替换系统 Node。
- Python：版本不足 3.12 时，通过固定版本 uv 安装项目专用 Python，不替换系统 Python；自动安装所需 venv 工具。

安装系统包时可能提示 **sudo 密码**，输入你的 Linux 用户密码即可。请使用普通用户执行 `bash run.sh`，**不要使用 `sudo bash run.sh`**；PostgreSQL 不能以 root 运行。首次安装需要联网；如果没有 sudo 权限，脚本会说明缺少的权限，不能跳过系统权限要求。

Scala 业务代码运行在 JVM 上，sbt 编译也需要 Java，因此安装 Java 是 Scala 工具链的一部分，并不要求编写 Java。

在 WSL 中，如果项目位于 `/mnt/c`、`/mnt/d` 等 Windows 盘，默认会将 PostgreSQL 数据放在 Linux 用户的状态目录，并在私有 `.env` 中保留该位置，避免 Windows 文件权限导致数据库启动失败。已有 `.env` 中明确设置的 `PG_DATA_DIR` 会优先使用。

使用已有数据库时可在 `.env` 设置 `MANAGE_POSTGRES=false` 和连接信息，自动安装逻辑会跳过 PostgreSQL 系统包。机器已有符合版本的工具时直接复用。不会修改你的 shell 配置文件或替换系统的 Node/Python。

配置优先级是环境变量 > `.env` > `config/defaults.json`。首次管理本地数据库时自动生成口令，保存在被 Git 忽略的 `.env`；没有外部付费 API 密钥要求。

### 开发与检查

需要单独操作时仍可使用原有脚本：

```bash
bash scripts/setup.sh              # 安装和构建
bash scripts/start-services.sh     # 只启动服务
bash scripts/build-backend.sh      # 只编译 Scala
npm --prefix frontend run dev     # 前端热更新，默认 5173
npm --prefix frontend run build   # 前端生产构建
```

源码下载不包含运行中的进程、数据库口令或依赖缓存；首次运行将创建这些本地状态。发布云环境快照后恢复时，也需要重新执行启动命令。

## 服务与数据归属

| 服务 | 技术 / 端口 | 业务职责 / 数据归属 |
|---|---|---|
| market | Scala 3 / 8101 | 股票、日线、历史指标；拥有 `market` schema |
| portfolio | Scala 3 / 8102 | 自选、研究报告；拥有 `portfolio` schema |
| analysis | Scala 3 / 8103 | 分析请求与参数校验；HTTP 调用行情和数值服务，无业务表 |
| quant | Python / 8104 | 纯数值计算；不访问数据库，不调用外部网络 |
| PostgreSQL | 17 / 55432 | 独立 schema，开发实例共享本地数据库 |

三个 Scala 服务为**不同进程、不同端口**，共享构建产物，通过 `SERVICE` 选择服务入口。并非只把文件夹命名为“微服务”。该课程版采用同一个本地数据库用户，schema 表示维护归属，不提供生产级安全隔离。前端是一个本地共享研究空间，没有登录和用户权限系统。

[架构与课程要求对照](docs/COURSE-ALIGNMENT.md) · [原始实施计划](docs/PLAN.md) · [数据与指标口径](docs/DATA-AND-METHODS.md) · [验证记录](docs/VALIDATION.md)

## 数据说明

用户 Release `data_v1` 的 `part1.zip` 已完整下载并匹配发布 SHA256；选取其中 32 个跨行业股票/ADR/黄金 ETF，将约 1,300 万条源分钟记录简化为 **37,247 条日线**，覆盖 **2022-03-07 至 2026-10-23**。原始 ZIP 被忽略，不进入源代码包；可直接从已保存的 CSV 重建数据库。

- [日线 CSV](data/daily.csv)、[股票资料](data/stocks.json)、[逐股审计与来源](data/provenance.json) 已保留。
- `part2.zip`、`part3.zip` 没有导入。当前支持查询的是已导入的 32 个标的，不能声称覆盖整个美股市场。
- **没有财报、复权说明和分红数据**。PE、PB、ROE 等显示“未提供”；本软件的“历年指标”首先是行情与收益风险指标。
- 不能把分钟来源成交量当作全市场成交量，不能把未确认复权的价格收益当作总收益。

重新从原始包生成：

```bash
.venv/bin/python scripts/prepare_data.py --archive data/raw/part1.zip
python3 scripts/check-data.py
```

## 验证命令

服务启动后：

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m unittest discover -s quant/tests -v
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/verify-api.py
npm --prefix frontend run typecheck
npm --prefix frontend run build
cd frontend && npm run test:e2e
```

浏览器测试使用系统 Chromium；其他机器可以设置 `CHROMIUM_PATH`。测试会暂时写入自选/报告并清理，建议在开发数据库运行。界面截图位于 [docs/screenshots](docs/screenshots)。

## 范围

这是可运行的课程研究软件。没有实盘交易、自动行情更新、全市场因子数据、真实财报或账户系统。高阶矩优化为样本估计，MVSK 非凸，多起点求解不保证全局最优。请用回测和审计数据讨论方法，不以某次历史表现作为投资结论。

## 目录与连接配置

项目可以解压到任意可写目录（包括带空格的目录）。上述 `cd financial-terminal` 是相对于解压目录的示例；请按自己的位置进入项目，而非创建 `/workspace`。脚本根据自身位置定位项目，数据路径相对于项目根目录解析。

默认值统一放在 `config/defaults.json`。可复制 `.env.example` 为 `.env`，只填写需要覆盖的项；优先级为 **进程环境变量 > .env > 默认值**。数据库口令不会进入 Git。服务、前端及验证脚本读取同一份配置。

```bash
# 从项目目录启动，并临时覆盖端口（也可以写入 .env）
MARKET_PORT=8201 PORTFOLIO_PORT=8202 ANALYSIS_PORT=8203 QUANT_PORT=8204 FRONTEND_PORT=4273 bash scripts/start-services.sh
```

可配置 `DATA_DIR`、`PG_DATA_DIR`、`PG_BIN`、`PG_SHARE`、`PG_SOCKET_DIR`、`DB_HOST/PORT/NAME/USER/PASSWORD`、各服务端口与 `MARKET_URL/QUANT_URL`。端口是可覆盖的默认值，不是必须占用的固定端口。更改运行服务的配置前，先使用原配置停止进程。

已有 PostgreSQL：在 `.env` 设置 `MANAGE_POSTGRES=false` 和数据库连接信息，提前建立空数据库并授予表创建权限；脚本将验证连接，且不会启动、停止或初始化外部 PostgreSQL。需要非默认 PostgreSQL 安装位置时设置 `PG_BIN`；启动脚本自动定位已下载包内的可执行文件，不绑定版本目录。

搬移已经安装过的项目之前先停止服务。启动时会检查 Java classpath 的生成位置，位置变化或依赖失效时自动重建；这类绝对路径只存在于忽略的运行缓存。Python 虚拟环境本身不保证可搬移，请在新目录重新执行 setup（需要时先移除旧 `.venv` 后重建）。

浏览器测试优先使用 `CHROMIUM_PATH`，其次搜索 PATH，最后使用 Playwright 自己安装的 Chromium，不依赖 `/usr/bin/chromium`。
