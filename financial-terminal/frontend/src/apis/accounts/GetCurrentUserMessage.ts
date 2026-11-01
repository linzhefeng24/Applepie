import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetCurrentUserMessage extends APIMessage<{user: User}> {
 readonly service = "accounts" as const;
 constructor() { super(); }
}
