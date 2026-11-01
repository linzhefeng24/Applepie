import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetBootstrapInfoMessage extends APIMessage<{initialized: boolean}> {
 readonly service = "accounts" as const;
 constructor() { super(); }
}
