import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetSecurityMessage extends APIMessage<Market["stocks"][number]> {
 readonly service = "catalog" as const;
 constructor(public symbol: string) { super(); }
}
