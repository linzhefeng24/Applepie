package services.watchlist.api
import services.watchlist.objects.apiTypes.WatchlistResponse
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.APIMessage
import services.watchlist.tables.WatchlistTable.WatchlistTable
final case class SetWatchlistMessage(userId:String,symbol: String, selected: Boolean)
    extends APIMessage[WatchlistResponse]:
  def plan(connection: Connection): IO[WatchlistResponse] =
    services.system.http.ServiceClient.post("catalog","getsecurity",Json.obj("symbol"->symbol.asJson)) *> IO(require(symbol.matches("[A-Z][A-Z0-9.-]{0,11}"), "无效股票代码")) *>
      (if selected then WatchlistTable.add(connection,userId, symbol)
       else WatchlistTable.remove(connection,userId, symbol)) *>
      WatchlistTable.list(connection,userId).map(xs => WatchlistResponse(xs))
object SetWatchlistMessage:
  given Decoder[SetWatchlistMessage] = deriveDecoder
