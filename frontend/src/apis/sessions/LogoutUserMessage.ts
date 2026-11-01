import {APIMessage} from "../APIMessage";
import type {Market, Bar, Metrics, Annual} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class LogoutUserMessage extends APIMessage<{loggedOut: boolean}> {
 readonly service = "sessions" as const;
 constructor() { super(); }
}
