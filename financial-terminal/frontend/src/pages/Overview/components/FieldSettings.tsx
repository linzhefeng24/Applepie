import { useState } from "react";
import { X, ChevronUp, ChevronDown } from "lucide-react";
import { fields, presets } from "../functions/marketMath";
export function FieldSettings({
  ids,
  onChange,
  close,
}: {
  ids: string[];
  onChange: (ids: string[]) => void;
  close: () => void;
}) {
  const [fieldQuery, setFieldQuery] = useState("");
  const columns = ids
    .map((id) => fields.find((f) => f.id === id)!)
    .filter(Boolean);
  const change = ({ columns }: { columns: string[] }) => onChange(columns);
  return (
    <div className="fields-backdrop" onClick={() => close()}>
      <section
        role="dialog"
        aria-label="字段设置"
        className="fields-drawer"
        onClick={(e) => e.stopPropagation()}
      >
        <header>
          <strong>字段设置</strong>
          <span>
            {columns.length} / {fields.length}
          </span>
          <button aria-label="关闭字段设置" onClick={() => close()}>
            <X size={14} />
          </button>
        </header>
        <input
          aria-label="搜索指标"
          placeholder="搜索字段"
          value={fieldQuery}
          onChange={(e) => setFieldQuery(e.target.value)}
        />
        <div className="field-presets">
          {Object.keys(presets).map((name) => (
            <button
              key={name}
              onClick={() => change({ columns: presets[name] })}
            >
              {name}
            </button>
          ))}
        </div>
        <p>勾选显示字段；↑ ↓ 调整列顺序。配置自动保存在当前浏览器。</p>
        <div className="chosen-fields">
          {columns.map((f, i) => (
            <div key={f.id}>
              <span>
                {i + 1}. {f.label}
              </span>
              <button
                disabled={i === 0}
                aria-label={`左移 ${f.label}`}
                onClick={() => {
                  const next = [...ids];
                  [next[i - 1], next[i]] = [next[i], next[i - 1]];
                  change({ columns: next });
                }}
              >
                <ChevronUp size={12} />
              </button>
              <button
                disabled={i === columns.length - 1}
                aria-label={`右移 ${f.label}`}
                onClick={() => {
                  const next = [...ids];
                  [next[i + 1], next[i]] = [next[i], next[i + 1]];
                  change({ columns: next });
                }}
              >
                <ChevronDown size={12} />
              </button>
              <button
                aria-label={`隐藏 ${f.label}`}
                disabled={columns.length === 1}
                onClick={() =>
                  change({
                    columns: ids.filter((id) => id !== f.id),
                  })
                }
              >
                <X size={11} />
              </button>
            </div>
          ))}
        </div>
        {["行情", "收益", "风险", "技术"].map((group) => (
          <fieldset key={group}>
            <legend>{group}</legend>
            {fields
              .filter(
                (f) =>
                  f.group === group &&
                  `${f.label} ${f.description}`
                    .toLowerCase()
                    .includes(fieldQuery.toLowerCase()),
              )
              .map((f) => (
                <label key={f.id} title={f.description}>
                  <input
                    type="checkbox"
                    aria-label={`显示 ${f.label}`}
                    checked={ids.includes(f.id)}
                    disabled={ids.includes(f.id) && columns.length === 1}
                    onChange={() =>
                      change({
                        columns: ids.includes(f.id)
                          ? ids.filter((id) => id !== f.id)
                          : [...ids, f.id],
                      })
                    }
                  />
                  <span>
                    {f.label}
                    <small>{f.description}</small>
                  </span>
                </label>
              ))}
          </fieldset>
        ))}
        <div className="unavailable-fields">
          财报字段：PE / PB / ROE / 市值
          <br />
          源数据未提供，暂不可选。
        </div>
      </section>
    </div>
  );
}
