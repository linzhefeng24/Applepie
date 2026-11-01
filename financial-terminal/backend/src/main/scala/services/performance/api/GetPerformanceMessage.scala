package services.performance.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.StatelessMessage
import services.system.http.ServiceClient
import services.system.analytics.ReturnMath
import services.daily.objects.DailyBar
final case class GetPerformanceMessage(symbol:String,start:String,end:String) extends StatelessMessage[Json]:
  def plan: IO[Json] =
    for
      prices<-ServiceClient.post("daily","getprices",Json.obj("symbols"->List(symbol).asJson,"start"->start.asJson,"end"->end.asJson))
      bars<-IO.fromEither(prices.hcursor.downField("series").get[List[DailyBar]](symbol))
      summary=ReturnMath.summary(bars)
    yield Json.fromJsonObject(summary.asObject.get.filterKeys(Set("observations","totalReturn","annualReturn","mean")))
object GetPerformanceMessage:
  given Decoder[GetPerformanceMessage]=deriveDecoder
