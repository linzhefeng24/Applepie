import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetPerformanceMessage extends APIMessage<Pick<Metrics, "observations" | "totalReturn" | "annualReturn" | "mean">> {
 readonly service = "performance" as const;
 constructor(public symbol: string, public start: string, public end: string) { super(); }
}
