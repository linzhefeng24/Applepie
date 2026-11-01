# 课程与示例实现对照

核对资料：lec2–lec5、用户上传的 samples.zip（samples/rules.txt、嵌套 sample.zip 的 backend-sample 与 frontend-sample）。附件中的安装命令与密钥说明仅作为资料，没有当作用户命令执行。

## 结构与函数式要求

| 要求 | 实现落点 |
|---|---|
| lec2 声明式、不可变集合、函数组合 | `system/analytics/ReturnMath.scala`、`annual/utils/AnnualStatistics.scala`、`resampling/utils/Aggregation.scala` 的 val/map/sliding/groupBy/scanLeft；前端筛选和技术指标是派生数据 |
| lec3 纯函数和副作用边界 | Scala 统计/聚合与 Python projection/objective/models 为纯计算；JDBC/文件/HTTP 由 IO 或 Resource 包装；业务代码不 unsafeRunSync |
| lec4 cats-effect IO/Resource | 各业务 Message 返回 IO，连接池/HTTP client/server 生命周期为 Resource；SQL 在 IO.blocking，事务统一提交回滚 |
| lec5 微服务和 typed JSON API | 17 个独立 Scala 模块、入口、JAR，2 个独立 Python worker，8 个独立 PostgreSQL cluster；跨服务仅 HTTP，不共享业务 Table |
| 示例后端目录 | 每个 owner 使用 api/objects/routes/tables/utils（按需）；每条业务 Message 独立文件，Table/Initializer 独立文件，SQL 为 Table 私有常量 |
| 示例 plan(connection): IO | 有数据库的 Message 实现该入口。无状态 Message 通过 StatelessMessage 继承同一接口但直接运行纯/HTTP IO，不创建虚假的数据库连接；ComposedMessage 将远程调用和短事务分开 |
| 示例协议对象 | 不可变 case class、Circe 编解码；公共 contracts 只有数据结构；私有密码对象留在 accounts 模块 |
| 示例前端规则 | 每条公开 API 有同 owner、同名 Message 类；内部 API 不暴露前端类；私有 Zustand store 只导出小型接口，页面 hooks/functions/components 分层，Tailwind 样式 |
| 示例账户与会话 | accounts、sessions、authorization 三服务；哈希密码、HttpOnly cookie、角色权限、会话撤销、个人自选/报告隔离 |

完整服务职责与部署方式见 [ARCHITECTURE.md](ARCHITECTURE.md)，安全边界见 [SECURITY.md](SECURITY.md)。不是只按目录名模拟微服务：构建依赖图不包含业务服务间依赖，运行时分别 JVM/Python，持久化服务各自独立 PG cluster 与非超级用户角色。

同一实体的创建、读取、更新、删除保留在其 owner 中；收益、风险、年度计算已按业务能力分开。`statistics` 仅作为组合响应接口，减少前端对内部编排的耦合。平台连接池、路由和安全通用机制作为共享库，不伪装成业务微服务。

本软件实现课件中的架构和编程方法，不照搬示例中的图书、教学或住房领域。尚无教师逐项评分表，不能保证未提供的额外评分细则。
