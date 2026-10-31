package services.portfolio.objects.apiTypes
import io.circe.{Encoder, Decoder, Json}
import io.circe.generic.semiauto.*
final case class SaveReportResponse(id: String)
object SaveReportResponse:
  given Encoder[SaveReportResponse] = deriveEncoder
  given Decoder[SaveReportResponse] = deriveDecoder
