package services.catalog.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.APIMessage
import services.catalog.tables.StockTable.StockTable
final case class ListSecuritiesMessage() extends APIMessage[Json]:
  def plan(connection: Connection): IO[Json] =
    StockTable.list(connection).map(xs=>Json.obj("stocks"->xs.asJson))
object ListSecuritiesMessage:
  given Decoder[ListSecuritiesMessage]=deriveDecoder
