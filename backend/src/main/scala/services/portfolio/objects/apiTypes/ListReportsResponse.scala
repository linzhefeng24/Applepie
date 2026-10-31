package services.portfolio.objects.apiTypes
import io.circe.{Encoder, Decoder, Json}
import io.circe.generic.semiauto.*
final case class ListReportsResponse(reports: List[services.portfolio.objects.ResearchReport])
object ListReportsResponse:
  given Encoder[ListReportsResponse] = deriveEncoder
  given Decoder[ListReportsResponse] = deriveDecoder
