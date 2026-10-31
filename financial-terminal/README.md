# APERTURE · 金融研究终端

基于用户真实美股分钟行情的课程软件：检索与自选 → 个股年度指标与比较 → 五模型量化分析 → 滚动样本外回测 → 保存、导出研究报告。

## 已实现

- **研究概览**：32 个已导入标的、代码/名称检索、行业筛选、自选持久化、最近源价格与成交量。
- **个股研究**：历史价格、双股票共同日期归一比较、收益分布、2022–2026 年行情指标、数据质量。指标包括收益、波动、最大回撤、Sharpe、偏度、超额峰度。
- **量化实验室**：等权、最小方差、均值—方差、MVSK、风险平价；2–10 个标的、权重上限、高阶矩偏好、多起点优化与收敛状态、相关性热力图、权重与分布。
- **回测**：固定滚动估计窗口、滞后一整个收盘的信号、漂移持仓、交易费、同口径基准、净值与回撤、调仓审计、CSV 导出。
- **研究档案**：PostgreSQL 保存完整参数和结果；浏览、删除、Markdown / JSON 导出和浏览器打印为 PDF。
- 清楚区分加载、错误、空数据、计算中、就绪、求解失败回退；支持手机布局。

## 运行

已在当前云环境安装、构建和验证。使用现有 checkout，不需要创建 worktree。

```bash
cd financial-terminal
./scripts/start-services.sh
```

生产前端端口为 `4173`；该端口由 Vite preview 提供，用于课程本地演示。开发前端使用：

```bash
cd financial-terminal/frontend
npm run dev
```

开发前端端口为 `5173`，前后端请求由 Vite 代理。后端和计算服务仅监听本机。停止本项目服务：

```bash
cd financial-terminal
./scripts/stop-services.sh              # 保留数据库运行
./scripts/stop-services.sh --database   # 同时停止本项目数据库
```

修改 Scala 后先运行 `./scripts/build-backend.sh`，再停止并重启服务。修改前端后运行 `npm --prefix frontend run build` 更新生产演示构建。日常开发直接使用 Vite dev。

## 首次安装与复现

工具基线：Debian 13 x86_64（当前云环境）、JDK 21、Node 24、npm 11、Python 3.12、curl、dpkg-deb。安装脚本优先使用 `PG_BIN` 指定或 PATH 中的 PostgreSQL；未找到时，仅在 Debian 13 x86_64 自动下载经过哈希验证的本地包（无需 root）。其他 Linux 环境应先安装 PostgreSQL，或使用已有数据库。自动下载的 Debian 二进制依赖系统的 libpq/ICU/LLVM 等运行库，不作为跨平台发行包。

```bash
cd financial-terminal
./scripts/setup.sh
./scripts/start-services.sh
```

安装脚本校验固定的 sbt 和 PostgreSQL 下载哈希，使用锁文件安装前端，安装固定版本数值依赖，验证精简数据、构建前后端并执行数值测试。首次运行随机生成本地数据库口令并保存至被 Git 忽略的 `.env`，不包含外部 API 密钥。不要把 `.env` 提交到 Git。

恢复环境时保留依赖、数据库和文件，但进程需要重启。`start-services.sh` 会重新导入行情表（事务内刷新）而保留自选与报告；它是重复运行安全的。停止脚本只处理有归属记录且启动时间匹配的本项目进程。

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
