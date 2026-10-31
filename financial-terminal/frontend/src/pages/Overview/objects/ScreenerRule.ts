export type Rule = {
  id: number;
  field: string;
  operator: "gte" | "lte";
  value: string;
};
