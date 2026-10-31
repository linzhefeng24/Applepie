package services.market.objects.apiTypes
import io.circe.{Encoder, Decoder, Json}
import io.circe.generic.semiauto.*
final case class GetStockResponse(
    stock: services.market.objects.Stock,
    bars: List[services.market.objects.DailyBar],
    metrics: Json,
    annual: Json
)
object GetStockResponse:
  given Encoder[GetStockResponse] = deriveEncoder
  given Decoder[GetStockResponse] = deriveDecoder
