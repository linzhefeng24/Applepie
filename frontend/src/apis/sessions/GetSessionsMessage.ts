import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetSessionsMessage extends APIMessage<{sessions: Session[]}> {
 readonly service = "sessions" as const;
 constructor() { super(); }
}
