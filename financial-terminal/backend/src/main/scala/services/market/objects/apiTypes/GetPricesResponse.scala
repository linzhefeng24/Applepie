package services.market.objects.apiTypes
import io.circe.{Encoder, Decoder, Json}
import io.circe.generic.semiauto.*
final case class GetPricesResponse(series: Map[String, List[services.market.objects.DailyBar]])
object GetPricesResponse:
  given Encoder[GetPricesResponse] = deriveEncoder
  given Decoder[GetPricesResponse] = deriveDecoder
