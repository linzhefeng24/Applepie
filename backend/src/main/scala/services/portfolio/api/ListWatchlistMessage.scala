package services.portfolio.api
import services.portfolio.objects.apiTypes.WatchlistResponse
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.NoRequestMessage
import services.portfolio.tables.WatchlistTable.WatchlistTable
final case class ListWatchlistMessage() extends NoRequestMessage[WatchlistResponse]:
  def plan(connection: Connection): IO[WatchlistResponse] =
    WatchlistTable.list(connection).map(xs => WatchlistResponse(xs))
object ListWatchlistMessage:
  given Decoder[ListWatchlistMessage] = deriveDecoder
