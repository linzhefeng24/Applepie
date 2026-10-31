import { APIMessage } from "../APIMessage";

export class DeleteReportMessage extends APIMessage<{ deleted: boolean }> {
  readonly service = "portfolio" as const;
  constructor(public id: string) {
    super();
  }
}
