package services.watchlist.objects.apiTypes
import io.circe.{Encoder, Decoder, Json}
import io.circe.generic.semiauto.*
final case class WatchlistResponse(symbols: List[String])
object WatchlistResponse:
  given Encoder[WatchlistResponse] = deriveEncoder
  given Decoder[WatchlistResponse] = deriveDecoder
