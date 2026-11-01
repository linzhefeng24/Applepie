package services.daily.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.APIMessage
import services.daily.tables.DailyBarTable.DailyBarTable
final case class GetCoverageMessage(symbol:String) extends APIMessage[Json]:
  def plan(connection: Connection): IO[Json] =
    DailyBarTable.bounds(connection,symbol).map(_.fold(Json.Null){case (start,end,count)=>Json.obj("start"->start.asJson,"end"->end.asJson,"observations"->count.asJson)})
object GetCoverageMessage:
  given Decoder[GetCoverageMessage]=deriveDecoder
