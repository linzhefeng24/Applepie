import { APIMessage } from "../APIMessage";
import type { ResearchReport } from "../../objects/analysis";
export class ListReportsMessage extends APIMessage<{
  reports: ResearchReport[];
}> {
  readonly service = "portfolio" as const;
  constructor() {
    super();
  }
}
