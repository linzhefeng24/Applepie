package services.annual.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.StatelessMessage
import services.system.http.ServiceClient
import services.daily.objects.DailyBar
import services.annual.utils.AnnualStatistics
final case class GetAnnualMessage(symbol:String,start:String,end:String) extends StatelessMessage[Json]:
  def plan: IO[Json] =
    ServiceClient.post("daily","getprices",Json.obj("symbols"->List(symbol).asJson,"start"->start.asJson,"end"->end.asJson)).flatMap(j=>IO.fromEither(j.hcursor.downField("series").get[List[DailyBar]](symbol))).map(AnnualStatistics.annual)
object GetAnnualMessage:
  given Decoder[GetAnnualMessage]=deriveDecoder
