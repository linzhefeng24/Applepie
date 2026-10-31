import type { Dispatch, SetStateAction } from "react";
import { X, Plus } from "lucide-react";
import { fields } from "../functions/marketMath";
import type { Rule } from "../objects/ScreenerRule";
export function RuleBuilder({
  rules,
  setRules,
}: {
  rules: Rule[];
  setRules: Dispatch<SetStateAction<Rule[]>>;
}) {
  return (
    <div className="screen-rules">
      <span>同时满足</span>
      {rules.map((rule) => (
        <div key={rule.id}>
          <select
            aria-label="筛选指标"
            value={rule.field}
            onChange={(e) =>
              setRules((list) =>
                list.map((r) =>
                  r.id === rule.id ? { ...r, field: e.target.value } : r,
                ),
              )
            }
          >
            {fields.map((f) => (
              <option key={f.id} value={f.id}>
                {f.label}
                {f.format === "percent" ? " (%)" : ""}
              </option>
            ))}
          </select>
          <select
            aria-label="筛选运算符"
            value={rule.operator}
            onChange={(e) =>
              setRules((list) =>
                list.map((r) =>
                  r.id === rule.id
                    ? {
                        ...r,
                        operator: e.target.value as Rule["operator"],
                      }
                    : r,
                ),
              )
            }
          >
            <option value="gte">≥</option>
            <option value="lte">≤</option>
          </select>
          <input
            aria-label="筛选阈值"
            type="number"
            value={rule.value}
            onChange={(e) =>
              setRules((list) =>
                list.map((r) =>
                  r.id === rule.id ? { ...r, value: e.target.value } : r,
                ),
              )
            }
          />
          <button
            aria-label="删除筛选条件"
            onClick={() =>
              setRules((list) => list.filter((r) => r.id !== rule.id))
            }
          >
            <X size={11} />
          </button>
        </div>
      ))}
      <button
        onClick={() =>
          setRules((list) => [
            ...list,
            {
              id: Date.now(),
              field: "volatility",
              operator: "lte",
              value: "",
            },
          ])
        }
      >
        <Plus size={11} />
        添加条件
      </button>
      {rules.length > 0 && <button onClick={() => setRules([])}>清空</button>}
    </div>
  );
}
