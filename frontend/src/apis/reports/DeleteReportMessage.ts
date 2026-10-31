import { APIMessage } from "../APIMessage";

export class DeleteReportMessage extends APIMessage<{ deleted: boolean }> {
  readonly service = "reports" as const;
  constructor(public id: string) {
    super();
  }
}
