import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetAnnualMessage extends APIMessage<Annual[]> {
 readonly service = "annual" as const;
 constructor(public symbol: string, public start: string, public end: string) { super(); }
}
