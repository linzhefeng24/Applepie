package services.portfolio.objects.apiTypes
import io.circe.{Encoder, Decoder, Json}
import io.circe.generic.semiauto.*
final case class DeleteReportResponse(deleted: Boolean)
object DeleteReportResponse:
  given Encoder[DeleteReportResponse] = deriveEncoder
  given Decoder[DeleteReportResponse] = deriveDecoder
