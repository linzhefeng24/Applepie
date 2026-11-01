# 独立服务架构

19 个业务进程：17 个 Scala/JVM 服务，2 个 Python 数值进程。每个服务有独立端口、路由、日志、生命周期与发布入口。服务清单唯一来源为 `config/services.json`。

| 服务 | 默认 HTTP 端口 | 单一业务职责 | 数据所有权 |
|---|---:|---|---|
| catalog | 8101 | 证券目录 | 独立 PostgreSQL，55441 |
| quotes | 8110 | 最新历史行情快照 | 无数据库 |
| provenance | 8111 | 数据来源审计 | 无数据库 |
| daily | 8106 | 日线存储查询 | 独立 PostgreSQL，55442 |
| minute | 8112 | 分钟存储查询 | 独立 PostgreSQL，55443 |
| resampling | 8113 | 多频率聚合 | 无数据库 |
| statistics | 8107 | 证券分析响应编排 | 无数据库 |
| performance | 8114 | 收益指标 | 无数据库 |
| risk | 8115 | 风险指标 | 无数据库 |
| annual | 8116 | 年度指标 | 无数据库 |
| watchlist | 8102 | 用户自选证券 | 独立 PostgreSQL，55444 |
| reports | 8108 | 用户研究报告 | 独立 PostgreSQL，55445 |
| optimization | 8103 | 组合优化请求编排 | 无数据库 |
| backtest | 8105 | 回测请求编排 | 无数据库 |
| accounts | 8109 | 账户与密码 | 独立 PostgreSQL，55446 |
| sessions | 8117 | 登录会话 | 独立 PostgreSQL，55447 |
| authorization | 8118 | 角色与权限 | 独立 PostgreSQL，55448 |
| quant_optimizer | 8104 | 数值优化 | 无数据库 |
| quant_backtest | 8119 | 数值回测 | 无数据库 |

`quotes` 的“最新”是已导入历史数据的末日，不是实时行情。`statistics` 只负责组合证券资料、价格、收益、风险、年度结果；计算分别属于 performance/risk/annual。自选、报告、账户等同一实体的增删改查保持在一个服务中，不按 SQL 动词拆成服务。

## 构建与部署

`backend/build.sbt` 是多项目构建：contracts 为不可变数据与编码协议，platform 为 HTTP、连接池、安全等基础设施，17 个 business project 分别依赖这两个公共库，互不依赖其他服务实现。contracts 不包含私有 StoredUser 或密码散列。

每个 Scala 服务有自己的 `services/<owner>/routes/ServiceMain.scala`。可独立编译，例如 `scripts/sbt.sh 'risk / compile'`；完整构建 `scripts/build-backend.sh`。`scripts/backend-runtime.py pack` 输出 17 个 `backend/runtime/services/<owner>.jar`、两个共享基础库和去重的第三方依赖，清单记录每个服务自己的 mainClass/classpath/SHA256。不存在包含全部业务实现的应用 JAR。

`python3 scripts/package-service.py risk /tmp/aperture-risk.zip` 导出一个独立发布包，只包含 risk 实现、平台/协议和必要依赖；按包内 README 导出环境变量后 `bash run.sh`。它不包含其他业务服务实现、数据库口令、服务令牌。完整安装包为本地启动方便，在同一机器编排所有独立进程。

## 数据隔离

本地默认启动八个不同的 PostgreSQL cluster，分别有独立数据目录、端口、应用角色和随机口令。应用角色不是超级用户。每个服务只得到自己数据库的连接配置；无数据库服务和 Python 进程不接收 DB_* 配置。跨服务数据查询通过 HTTP API；不存在跨服务 Table 导入、跨库外键或共享 Connection。

默认持久化目录是 `PG_DATA_DIR` 的同级 `services/`；WSL 的 Windows 盘项目会自动放入 Linux 用户状态目录。可用 `SERVICE_STATE_DIR` 显式设置。私有 credentials.json 为 0600、父目录为 0700；进程私有配置在忽略的 `.run/service-env/`。公开日志不打印口令。

`MANAGE_POSTGRES=false` 时为每个有状态服务配置 `<SERVICE>_DB_HOST/PORT/NAME/USER/PASSWORD`，以连接不同主机上的实例。HTTP 地址也可用 `<SERVICE>_URL` 独立指定。本地独立 cluster 仍共享 OS 用户与主机，不等于容器/虚拟机级的对抗性安全隔离；正式多机部署应进一步使用独立系统身份、网络策略和 HTTPS。

## 跨服务通信

```
Frontend → catalog / quotes / provenance / resampling / statistics
quotes → daily
resampling → daily + minute
statistics → catalog + daily + performance + risk + annual
performance / risk / annual → daily
optimization → daily + quant_optimizer
backtest → daily + quant_backtest
accounts → authorization + sessions
各受保护公开入口 → sessions + authorization
sessions / authorization → accounts 内部身份契约
watchlist → catalog（校验证券）
```

所有 Scala 内部调用使用 http4s Resource 客户端；短数据库事务结束后再进行远程账号流程，不占着连接池等待其他服务。每个调用方使用不同的随机 token；接收方只持有允许调用方 token 的 SHA256。内部身份管理消息还校验 caller allowlist。Python optimizer 只接受 optimization，Python backtest 只接受 backtest；两个 worker 无数据库导入，各自只注册一个业务路由。

## 数值代码

`quant/optimization/models/` 每种优化模型一个模块；目标函数、约束投影、求解和分析编排分别在对应模块。`quant/backtesting/` 单独维护回测与模拟循环。`quant/shared/` 只含验证、对齐和纯统计函数。`quant/engine.py` 仅为旧测试/脚本保留兼容导出。回测 worker 在本进程复用优化纯函数库，不调用优化 worker，也不共享计算进程。
