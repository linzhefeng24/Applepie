# API reference

所有公开业务请求：`POST /api/<service>/<message-name-lowercase-without-Message>`，`Content-Type: application/json`。运行中的每个 Scala 服务提供 `GET /api/<service>/openapi.json`；健康检查 `GET /health`。端口与部署边界见 [ARCHITECTURE.md](ARCHITECTURE.md)。前端反向代理只开放 `/api/<service>`，不代理 `/internal`。

## 登录

第一次在 UI 注册管理员。命令行使用自己创建的账号（示例中的凭据是占位符）：

```sh
curl -c cookies.txt -H 'Content-Type: application/json' \
  --data '{"username":"YOUR_ACCOUNT","password":"YOUR_PASSWORD"}' \
  http://127.0.0.1:4173/api/accounts/loginuser
curl -b cookies.txt -H 'Content-Type: application/json' \
  --data '{"symbol":"AAPL","start":"2026-10-23","end":"2026-10-23","frequency":"2min"}' \
  http://127.0.0.1:4173/api/resampling/getbars
```

密码和 cookie 文件由使用者妥善保管，不提交 Git。会话令牌只通过 HttpOnly cookie 返回，登录响应 JSON 包含 user 与 expiresAt。角色变化、停用和密码版本每次请求重新核验。外部请求禁止指定 userId/role/identity/sessionToken；所有用户归属由服务端解析。

## 公开消息

| Service | Endpoint | 请求字段 | 必要权限 |
|---|---|---|---|
| accounts | `registeruser` | `username`, `password`, `displayName` | public |
| accounts | `loginuser` | `username`, `password` | public |
| accounts | `getbootstrapinfo` | `{}` | public |
| accounts | `getcurrentuser` | `{}` | profile:self |
| accounts | `updateprofile` | `displayName` | profile:self |
| accounts | `changepassword` | `currentPassword`, `newPassword` | profile:self |
| annual | `getannual` | `symbol`, `start`, `end` | data:read |
| authorization | `listusers` | `{}` | users:manage |
| authorization | `setaccess` | `targetUserId`, `newRole`, `enabled` | users:manage |
| backtest | `runbacktest` | `parameters` | research:compute |
| catalog | `listsecurities` | `{}` | data:read |
| catalog | `getsecurity` | `symbol` | data:read |
| daily | `getprices` | `symbols`, `start`, `end` | data:read |
| daily | `getcoverage` | `symbol` | data:read |
| daily | `gettailbars` | `{}` | data:read |
| minute | `getminuteprices` | `symbol`, `start`, `end` | data:read |
| minute | `getcoverage` | `symbol` | data:read |
| optimization | `runanalysis` | `parameters` | research:compute |
| performance | `getperformance` | `symbol`, `start`, `end` | data:read |
| provenance | `getprovenance` | `{}` | data:read |
| quotes | `listquotes` | `{}` | data:read |
| reports | `listreports` | `{}` | reports:read |
| reports | `savereport` | `title`, `kind`, `parameters`, `result` | reports:write |
| reports | `deletereport` | `id` | reports:write |
| resampling | `getbars` | `symbol`, `start`, `end`, `frequency` | data:read |
| resampling | `listfrequencies` | `symbol` | data:read |
| risk | `getrisk` | `symbol`, `start`, `end` | data:read |
| sessions | `getsessions` | `{}` | sessions:self |
| sessions | `logoutuser` | `{}` | sessions:self |
| sessions | `logoutall` | `{}` | sessions:self |
| sessions | `revokesession` | `sessionId` | sessions:self |
| statistics | `getstock` | `symbol`, `start`, `end` | data:read |
| watchlist | `listwatchlist` | `{}` | watchlist:read |
| watchlist | `setwatchlist` | `symbol`, `selected` | watchlist:write |

默认 analyst 可使用所有研究接口，viewer 可读取，admin 额外管理用户。完整角色表见 [SECURITY.md](SECURITY.md)。公开响应的 TypeScript 类型在 `frontend/src/apis/<service>/<Message>.ts`，Scala 编解码在对应 api 与 objects 文件。

## 数据契约

- catalog 返回 `{stocks:[Stock]}`，quotes 返回 `{quotes:{symbol:{date,close,volume,changePct}}}`，provenance 直接返回来源审计对象。前端将三份响应组合为行情状态。
- daily/getprices 返回 `{series:{symbol:[{date,open,high,low,close,volume,minutes}]}}`。start/end 为包含端点的 yyyy-MM-dd，每次最多十个标的。daily/gettailbars 返回每只最后两根日线，供快照服务使用。
- minute/getminuteprices 返回 `{bars:[...]}`，保留无时区标记的源时间；单次原始分钟上限 50000。minute/daily 的 getcoverage 返回 start/end/observations 或 null。
- resampling/getbars 返回 symbol、frequency、sourceResolution、bars、requestedStart/requestedEnd、incompleteBars；1y/1mo/1d/5min/2min/1min，最多5000根聚合K线，不补造缺失分钟。年份跨度不足时年频不可用。listfrequencies 返回各频率 availability、真实覆盖和提示。
- statistics/getstock 返回 stock/bars/metrics/annual；收益、风险和年度分别来自 performance/risk/annual。不存在把财务报表指标伪装为行情计算指标。
- optimization/runanalysis 和 backtest/runbacktest 接收 `{parameters: AnalysisParameters}`。数值模型：equal/minvariance/meanvariance/riskparity/mvsk；保持日频收益与252交易日年化，切换展示K线频率不会偷偷改变回测假设。
- watchlist 返回当前用户的 `{symbols:[]}`。reports 查询返回本人 `{reports:[]}`；保存返回 id；删除只影响本人匹配的记录，重复删除幂等，不泄露他人记录是否存在。

错误 JSON 为 `{error:string}`；400 输入错误，401 无效/过期会话，403 权限或来源拒绝，404 未知消息，413 请求体过大，415 内容类型不符，429 计算忙，503 下游不可用。请求体上限8MB。内部账号与会话消息需要服务凭据及 caller allowlist，不属于浏览器公开 API。
