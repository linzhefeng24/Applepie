package services.reports.objects.apiTypes
import io.circe.{Encoder, Decoder, Json}
import io.circe.generic.semiauto.*
final case class ListReportsResponse(reports: List[services.reports.objects.ResearchReport])
object ListReportsResponse:
  given Encoder[ListReportsResponse] = deriveEncoder
  given Decoder[ListReportsResponse] = deriveDecoder
