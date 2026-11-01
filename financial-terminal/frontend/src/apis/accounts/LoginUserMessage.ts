import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class LoginUserMessage extends APIMessage<{user: User}> {
 readonly service = "accounts" as const;
 constructor(public username: string, public password: string) { super(); }
}
