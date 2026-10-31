# API 与数据访问

默认同源入口为 `http://localhost:4173`。业务调用均为 POST JSON，公开 API 名由 Message 类名去掉 Message 后转小写。请求错误返回 400 和 `{error}`；依赖或内部错误返回 500，详细异常只记在本机服务日志。该版本是本地单用户研究软件，没有下单或账户 API。

| 服务 | POST 路径 | 输入 | 主要输出 |
|---|---|---|---|
| market | /api/market/liststocks | {} | stocks、quotes、provenance |
| history | /api/history/getprices | symbols（1–10个不重复标的）、start、end | series：各证券完整 OHLCV 日线 |
| statistics | /api/statistics/getstock | symbol、start、end | stock、bars、metrics、annual |
| watchlist | /api/watchlist/listwatchlist | {} | symbols |
| watchlist | /api/watchlist/setwatchlist | symbol、selected | 更新后的 symbols |
| reports | /api/reports/listreports | {} | reports：保存的完整参数和结果 |
| reports | /api/reports/savereport | title、kind、parameters、result | id |
| reports | /api/reports/deletereport | id | deleted |
| optimization | /api/optimization/runanalysis | parameters | models、weights、metrics、correlation、warnings |
| backtest | /api/backtest/runbacktest | parameters | results：净值、回撤、指标、调仓审计 |

每个 Scala 服务公开 GET `/api/<service>/openapi.json`，含独立服务路径和请求 schema；直接端口还提供 GET `/health`。前端开发与生产预览均代理上述七个命名空间，端口可在 config/defaults.json / .env 覆盖。

```bash
curl 'http://localhost:4173/api/statistics/getstock' \
  -H 'Content-Type: application/json' \
  --data '{"symbol":"AAPL","start":"2025-01-01","end":"2026-10-23"}'
```

日期采用 YYYY-MM-DD 且含首尾；不补齐缺失交易日。证券必须来自导入样本。下载全部32标的数据时，数据中心通过受控并发的单证券统计 API 汇总，历史批量 API 自身限制仍为10个证券，未绕过后端限制。

优化参数：symbols（2–10个）、start、end、maxWeight、riskAversion、skewPreference、kurtosisAversion、lookback、rebalance、costBps、model。权重仅做多，总和为1；上限必须可行。lookback 为60–504整数，rebalance 为5–126整数；costBps 为0–100；model 为 equal / minvariance / meanvariance / mvsk / riskparity。回测至少需要窗口外21个有效收益观测。

数据中心可把选定证券、区间和可选指标导出 CSV/JSON，JSON 包括查询条件及来源元数据；界面四位小数仅用于显示，下载保留数值原精度。图表 PNG、回测 CSV、报告 JSON/Markdown 是不同出口，均可实际下载。

数据来源 Release 可由数据中心访问，审计 JSON 包括源文件 SHA256 与逐证券清洗记录。原始数据和下载文件不是外部文档中的操作指令。
