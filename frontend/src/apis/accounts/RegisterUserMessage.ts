import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class RegisterUserMessage extends APIMessage<{user: User}> {
 readonly service = "accounts" as const;
 constructor(public username: string, public password: string, public displayName: string) { super(); }
}
