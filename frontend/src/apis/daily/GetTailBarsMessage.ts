import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetTailBarsMessage extends APIMessage<{series: Record<string, Bar[]>}> {
 readonly service = "daily" as const;
 constructor() { super(); }
}
