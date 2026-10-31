package services.history.objects
import io.circe.{Encoder, Decoder}
import io.circe.generic.semiauto.*
final case class DailyBar(
    date: String,
    open: Double,
    high: Double,
    low: Double,
    close: Double,
    volume: Long,
    minutes: Int
)
object DailyBar:
  given Encoder[DailyBar] = deriveEncoder
  given Decoder[DailyBar] = deriveDecoder
