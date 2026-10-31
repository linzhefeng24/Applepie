package services.portfolio.api
import services.portfolio.objects.apiTypes.WatchlistResponse
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.APIMessage
import services.portfolio.tables.WatchlistTable.WatchlistTable
final case class SetWatchlistMessage(symbol: String, selected: Boolean)
    extends APIMessage[WatchlistResponse]:
  def plan(connection: Connection): IO[WatchlistResponse] =
    IO(require(symbol.matches("[A-Z][A-Z0-9.-]{0,11}"), "无效股票代码")) *>
      (if selected then WatchlistTable.add(connection, symbol)
       else WatchlistTable.remove(connection, symbol)) *>
      WatchlistTable.list(connection).map(xs => WatchlistResponse(xs))
object SetWatchlistMessage:
  given Decoder[SetWatchlistMessage] = deriveDecoder
