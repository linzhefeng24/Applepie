import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetMinutePricesMessage extends APIMessage<{bars: Bar[]}> {
 readonly service = "minute" as const;
 constructor(public symbol: string, public start: string, public end: string) { super(); }
}
