import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetCoverageMessage extends APIMessage<{ start: string; end: string; observations: number } | null> {
 readonly service = "minute" as const;
 constructor(public symbol: string) { super(); }
}
