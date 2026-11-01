import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class ChangePasswordMessage extends APIMessage<{changed: boolean}> {
 readonly service = "accounts" as const;
 constructor(public currentPassword: string, public newPassword: string) { super(); }
}
