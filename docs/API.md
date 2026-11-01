# API 与数据访问

默认同源入口为 `http://localhost:4173`。业务调用均为 POST JSON，公开 API 名由 Message 类名去掉 Message 后转小写。请求错误返回 400 和 `{error}`；依赖或内部错误返回 500，详细异常只记在本机服务日志。该版本是本地单用户研究软件，没有下单或账户 API。

| 服务 | POST 路径 | 输入 | 主要输出 |
|---|---|---|---|
| market | /api/market/liststocks | {} | stocks、quotes、provenance |
| history | /api/history/listfrequencies | symbol | 可用频率、真实日期范围、单次5000根上限 |
| history | /api/history/getbars | symbol、start、end、frequency | 真实OHLCV、源频率、缺失观测桶数 |
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


## 多频率数据

frequency 枚举：1y（年）、1mo（月）、1d（日）、5min、2min、1min。按 source 时间戳的自然日00:00对齐分钟桶；2/5分钟不跨日。open=首个真实观测，high=max，low=min，close=最后真实观测，volume=sum；minutes 为源分钟记录数量。空桶省略，缺少分钟的桶保留实际观测数量，不补齐。月/年按自然月/年由完整日线聚合；查询首尾可能为部分周期，时间标签是桶起点，可能早于查询起始日期。

默认分钟输入为32证券最近60个记录交易日（2026-07-31至2026-10-23，708997条），日线覆盖2022-03-07至2026-10-23。频率发现接口返回每只证券实际范围；不足三个完整公历年度时，不提供可选年线。图表分钟模式默认取所选区间末7个自然日，数据中心可以自定义范围。每证券每次最多5000根；超限返回400，不静默截断。

价格图选择频率与量化估计分开。筛选风险收益和优化/回测保持日频252期年化；没有把分钟、月或年数据套用日频年化公式。技术指标按当前K线根数计算，非日频数据下载仅使用本次查询到的K线预热，不足周期为null。
