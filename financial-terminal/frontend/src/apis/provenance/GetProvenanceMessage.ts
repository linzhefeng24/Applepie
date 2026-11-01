import {APIMessage} from "../APIMessage";
import type {Market} from "../../objects/market";
import type {User, Session} from "../../objects/auth";
export class GetProvenanceMessage extends APIMessage<Market["provenance"]> {
 readonly service = "provenance" as const;
 constructor() { super(); }
}
