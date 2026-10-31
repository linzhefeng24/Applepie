export abstract class APIMessage<T> {
  abstract readonly service: "market" | "analysis" | "portfolio";
  protected body(): unknown {
    const { service: _, ...fields } = this;
    return fields;
  }
  async send(signal?: AbortSignal): Promise<T> {
    // Production build preserves class names (vite minify:false); route names follow Scala Message names.
    const route = this.constructor.name.replace(/Message$/, "").toLowerCase();
    const response = await fetch(`/api/${this.service}/${route}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(this.body()),
      signal,
    });
    const data = await response.json();
    if (!response.ok)
      throw new Error(data.error || `请求失败 (${response.status})`);
    return data as T;
  }
}
