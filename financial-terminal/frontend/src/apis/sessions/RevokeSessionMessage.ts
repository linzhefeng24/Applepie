import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class RevokeSessionMessage extends APIMessage<{revoked: boolean}> {
 readonly service = "sessions" as const;
 constructor(public sessionId: string) { super(); }
}
