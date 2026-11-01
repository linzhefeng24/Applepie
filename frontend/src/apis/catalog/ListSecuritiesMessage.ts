import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class ListSecuritiesMessage extends APIMessage<{ stocks: Market["stocks"] }> {
 readonly service = "catalog" as const;
 constructor() { super(); }
}
