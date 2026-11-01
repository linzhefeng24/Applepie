import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class SetAccessMessage extends APIMessage<{updated: boolean}> {
 readonly service = "authorization" as const;
 constructor(public targetUserId: string, public newRole: string, public enabled: boolean) { super(); }
}
