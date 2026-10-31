package services.market.objects.apiTypes
import io.circe.{Encoder, Decoder, Json}
import io.circe.generic.semiauto.*
final case class ListStocksResponse(
    stocks: List[services.market.objects.Stock],
    quotes: Json,
    provenance: Json
)
object ListStocksResponse:
  given Encoder[ListStocksResponse] = deriveEncoder
  given Decoder[ListStocksResponse] = deriveDecoder
