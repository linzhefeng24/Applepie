export abstract class APIMessage<T> {
  abstract readonly service: "catalog" | "quotes" | "provenance" | "daily" | "minute" | "resampling" | "statistics" | "performance" | "risk" | "annual" | "watchlist" | "reports" | "optimization" | "backtest" | "accounts" | "sessions" | "authorization";
  protected body(): unknown {
    const { service: _, ...fields } = this;
    return fields;
  }
  async send(signal?: AbortSignal): Promise<T> {
    // Production build preserves class names (vite minify:false); route names follow Scala Message names.
    const route = this.constructor.name.replace(/Message$/, "").toLowerCase();
    const response = await fetch(`/api/${this.service}/${route}`, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(this.body()),
      signal,
    });
    const data = await response.json();
    if (!response.ok) {
      if (response.status === 401 && !["loginuser", "registeruser", "getcurrentuser"].includes(route)) window.dispatchEvent(new Event("aperture:unauthorized"));
      throw new Error(data.error || `请求失败 (${response.status})`);
    }
    return data as T;
  }
}
