import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Stock, StockResult } from "../../../objects/market";
import { Chart, axis } from "../../../components/ui/Chart";
import { technical, assetType, curves } from "../functions/marketMath";
import { number, percent } from "../../../utils/format";
export function SecurityDock({
  stock,
  data,
  start,
  end,
}: {
  stock: Stock;
  data?: StockResult;
  start: string;
  end: string;
}) {
  const [primary, setPrimary] = useState("MA"),
    [secondary, setSecondary] = useState("VOL"),
    [mode, setMode] = useState("candle"),
    [tab, setTab] = useState("年度指标");
  const nav = useNavigate();
  const [curve, setCurve] = useState("price");
  const history = data?.bars.filter((b) => b.date <= end) || [],
    bars = history.filter((b) => b.date >= start),
    last = history.at(-1),
    ta = technical(history),
    offset = history.length - bars.length;
  const paths = curves(history, start);
  const dates = bars.map((b) => b.date),
    line = (
      name: string,
      values: (number | null)[],
      color: string,
      sub = false,
    ) => ({
      name,
      type: "line",
      showSymbol: false,
      data: values.slice(offset),
      lineStyle: { width: 1, color },
      itemStyle: { color },
      xAxisIndex: sub ? 1 : 0,
      yAxisIndex: sub ? 1 : 0,
    });
  const hasSub = curve === "price" && secondary !== "NONE";
  const option = {
    animation: false,
    tooltip: { trigger: "axis", axisPointer: { type: "cross" } },
    legend: { top: 0, left: 45, textStyle: { color: "#8593a6", fontSize: 9 } },
    grid: [
      { left: 50, right: 40, top: 24, height: hasSub ? "53%" : "72%" },
      ...(hasSub ? [{ left: 50, right: 40, top: "72%", height: "16%" }] : []),
    ],
    xAxis: [
      {
        ...axis,
        type: "category",
        data: dates,
        axisLabel: { show: !hasSub, fontSize: 9 },
        boundaryGap: true,
      },
      ...(hasSub
        ? [
            {
              ...axis,
              type: "category",
              data: dates,
              gridIndex: 1,
              boundaryGap: true,
              axisLabel: { fontSize: 9, color: "#627088" },
            },
          ]
        : []),
    ],
    yAxis: [
      { ...axis, scale: true, position: "right", splitNumber: 3 },
      ...(hasSub
        ? [
            {
              ...axis,
              gridIndex: 1,
              position: "right",
              splitNumber: 1,
              min: secondary === "RSI" ? 0 : undefined,
              max: secondary === "RSI" ? 100 : undefined,
            },
          ]
        : []),
    ],
    dataZoom: [
      { type: "inside", xAxisIndex: hasSub ? [0, 1] : [0] },
      {
        type: "slider",
        xAxisIndex: hasSub ? [0, 1] : [0],
        height: 9,
        bottom: 0,
        borderColor: "transparent",
        fillerColor: "#e9b45b12",
        textStyle: { color: "#69778a", fontSize: 8 },
      },
    ],
    series: [
      mode === "candle"
        ? {
            name: stock.symbol,
            type: "candlestick",
            data: bars.map((b) => [b.open, b.close, b.low, b.high]),
            itemStyle: {
              color: "#55c9a3",
              color0: "#ee7c87",
              borderColor: "#55c9a3",
              borderColor0: "#ee7c87",
            },
          }
        : {
            name: stock.symbol,
            type: "line",
            showSymbol: false,
            data: bars.map((b) => b.close),
            lineStyle: { width: 1, color: "#c7d3df" },
          },
      ...(primary === "MA"
        ? [line("MA20", ta.ma20, "#d6b16d"), line("MA60", ta.ma60, "#7094ca")]
        : primary === "BOLL"
          ? [
              line("BOLL MID", ta.ma20, "#d6b16d"),
              line("BOLL UP", ta.upper, "#7094ca"),
              line("BOLL LOW", ta.lower, "#986c9b"),
            ]
          : []),
      ...(secondary === "VOL"
        ? [
            {
              name: "源成交量",
              type: "bar",
              xAxisIndex: 1,
              yAxisIndex: 1,
              data: bars.map((b) => ({
                value: b.volume,
                itemStyle: {
                  color: b.close >= b.open ? "#55c9a34a" : "#ee7c874a",
                },
              })),
            },
          ]
        : secondary === "RSI"
          ? [line("RSI14", ta.rsi, "#d6b16d", true)]
          : secondary === "MACD"
            ? [
                line("DIF", ta.dif, "#d6b16d", true),
                line("DEA", ta.dea, "#7094ca", true),
                {
                  name: "MACD ×2",
                  type: "bar",
                  xAxisIndex: 1,
                  yAxisIndex: 1,
                  data: ta.macd.slice(offset).map((value) => ({
                    value,
                    itemStyle: {
                      color: value >= 0 ? "#55c9a37a" : "#ee7c877a",
                    },
                  })),
                },
              ]
            : []),
    ],
  };
  const plotted =
    curve === "price"
      ? option
      : {
          ...option,
          legend: { show: false },
          series: [
            {
              name:
                curve === "return"
                  ? "累计价格收益 %"
                  : curve === "drawdown"
                    ? "区间回撤 %"
                    : "20日年化波动 %",
              type: "line",
              showSymbol: false,
              lineStyle: {
                width: 1.2,
                color: curve === "drawdown" ? "#ee7c87" : "#d6b16d",
              },
              data:
                curve === "return"
                  ? paths.cumulative
                  : curve === "drawdown"
                    ? paths.drawdown
                    : paths.volatility,
            },
          ],
        };
  return (
    <section className="security-dock" aria-label="联动证券分析">
      <div className="dock-title">
        <strong>{stock.symbol}</strong>
        <span>{stock.name}</span>
        <span>
          {assetType(stock)} · {stock.sector} · USD
        </span>
        <b>{number(last?.close)}</b>
        <small>{last?.date} · 历史源行情</small>
        <button onClick={() => nav("/stocks")}>证券分析 ↗</button>
      </div>
      <div className="dock-content">
        <div className="dock-chart">
          <div className="dock-chart-toolbar">
            <select
              aria-label="图表类型"
              value={mode}
              onChange={(e) => setMode(e.target.value)}
            >
              <option value="candle">日 K</option>
              <option value="line">收盘线</option>
            </select>
            <select
              aria-label="曲线指标"
              value={curve}
              onChange={(e) => setCurve(e.target.value)}
            >
              <option value="price">价格</option>
              <option value="return">累计收益</option>
              <option value="drawdown">回撤</option>
              <option value="volatility">滚动波动</option>
            </select>
            <label>主图</label>
            <select
              disabled={curve !== "price"}
              aria-label="主图指标"
              value={primary}
              onChange={(e) => setPrimary(e.target.value)}
            >
              <option value="NONE">无叠加</option>
              <option value="MA">MA20 / MA60</option>
              <option value="BOLL">BOLL (20, 2)</option>
            </select>
            <label>副图</label>
            <select
              disabled={curve !== "price"}
              aria-label="副图指标"
              value={secondary}
              onChange={(e) => setSecondary(e.target.value)}
            >
              <option value="NONE">无</option>
              <option value="VOL">源成交量</option>
              <option value="MACD">MACD (12,26,9)</option>
              <option value="RSI">RSI (14)</option>
            </select>
            <span>
              {start} — {end}
            </span>
          </div>
          {data && bars.length ? (
            <Chart
              label="联动历史行情图"
              height={210}
              option={plotted}
              exportName={`aperture-${stock.symbol}-${curve}`}
            />
          ) : (
            <div className="screen-empty">
              {data ? "当前区间没有行情" : "正在读取证券历史…"}
            </div>
          )}
        </div>
        <div className="dock-data">
          <div className="dock-tabs">
            {["年度指标", "数据口径"].map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={tab === t ? "active" : ""}
              >
                {t}
              </button>
            ))}
          </div>
          {tab === "年度指标" ? (
            <div className="dock-annual">
              <table>
                <thead>
                  <tr>
                    <th>年度（全历史）</th>
                    <th>价格收益</th>
                    <th>波动率</th>
                    <th>回撤</th>
                    <th>Sharpe</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.annual.map((y) => (
                    <tr key={y.year}>
                      <td>
                        {y.year}
                        {y.partial ? " *" : ""}
                      </td>
                      <td
                        className={y.totalReturn >= 0 ? "positive" : "negative"}
                      >
                        {percent(y.totalReturn)}
                      </td>
                      <td>{percent(y.volatility)}</td>
                      <td>{percent(y.maxDrawdown)}</td>
                      <td>{number(y.sharpe)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p>
                * 部分年度 ·
                使用完整可用历史；筛选表的风险指标按上方日期区间计算。
              </p>
            </div>
          ) : (
            <div className="dock-methodology">
              日线由有效源分钟聚合；复权方式未知、未计分红。成交量非全市场成交量。MA
              为简单均线；BOLL 使用20日总体标准差；RSI 为 Wilder 平滑；MACD
              使用首个收盘价初始化
              EMA，柱值为2×(DIF−DEA)。技术指标使用截至日期之前全部可用历史预热。不存在的指标显示
              —，不插值或补齐。
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
