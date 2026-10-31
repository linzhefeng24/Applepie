package services.reports.objects
import io.circe.{Encoder, Decoder, Json}
import io.circe.generic.semiauto.*
final case class ResearchReport(
    id: String,
    title: String,
    kind: String,
    createdAt: String,
    parameters: Json,
    result: Json
)
object ResearchReport:
  given Encoder[ResearchReport] = deriveEncoder
  given Decoder[ResearchReport] = deriveDecoder
