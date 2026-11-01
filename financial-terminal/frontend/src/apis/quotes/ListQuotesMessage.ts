import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class ListQuotesMessage extends APIMessage<{ quotes: Market["quotes"] }> {
 readonly service = "quotes" as const;
 constructor() { super(); }
}
