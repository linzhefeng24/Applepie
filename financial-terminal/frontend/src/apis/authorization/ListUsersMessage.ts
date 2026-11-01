import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class ListUsersMessage extends APIMessage<{users: User[]}> {
 readonly service = "authorization" as const;
 constructor() { super(); }
}
