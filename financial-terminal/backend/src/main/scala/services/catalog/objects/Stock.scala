package services.catalog.objects
import io.circe.{Encoder, Decoder}
import io.circe.generic.semiauto.*
final case class Stock(
    symbol: String,
    name: String,
    sector: String,
    currency: String,
    firstDate: String,
    lastDate: String,
    sessions: Int,
    source: String
)
object Stock:
  given Encoder[Stock] = deriveEncoder
  given Decoder[Stock] = deriveDecoder
