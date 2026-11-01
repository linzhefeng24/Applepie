import {ListSecuritiesMessage} from "../apis/catalog/ListSecuritiesMessage";
import {ListQuotesMessage} from "../apis/quotes/ListQuotesMessage";
import {GetProvenanceMessage} from "../apis/provenance/GetProvenanceMessage";
import type {Market} from "../objects/market";
export async function loadMarket(signal?: AbortSignal): Promise<Market> {
 const [catalog, quotes, provenance] = await Promise.all([new ListSecuritiesMessage().send(signal),new ListQuotesMessage().send(signal),new GetProvenanceMessage().send(signal)]);
 return {...catalog,...quotes,provenance};
}
