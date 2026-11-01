import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetRiskMessage extends APIMessage<Pick<Metrics, "observations" | "volatility" | "sharpe" | "maxDrawdown" | "variance" | "skewness" | "excessKurtosis">> {
 readonly service = "risk" as const;
 constructor(public symbol: string, public start: string, public end: string) { super(); }
}
