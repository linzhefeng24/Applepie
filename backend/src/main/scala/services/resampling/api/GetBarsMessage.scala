package services.resampling.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.StatelessMessage
import services.system.http.ServiceClient
import services.resampling.utils.{Aggregation,Validation}
import services.daily.objects.DailyBar
import services.resampling.objects.apiTypes.GetBarsResponse
final case class GetBarsMessage(symbol:String,start:String,end:String,frequency:String) extends StatelessMessage[services.resampling.objects.apiTypes.GetBarsResponse]:
  def plan: IO[services.resampling.objects.apiTypes.GetBarsResponse] =
    for
      _<-IO(Validation.dates(start,end))
      meta<-ListFrequenciesMessage(symbol).plan
      _<-IO(require(meta.frequencies.exists(f=>f.code==frequency&&f.available),"此频率无真实数据或历史跨度不足"))
      minute=frequency.endsWith("min")
      source<-if minute then ServiceClient.post("minute","getminuteprices",Json.obj("symbol"->symbol.asJson,"start"->start.asJson,"end"->end.asJson)).flatMap(j=>IO.fromEither(j.hcursor.get[List[DailyBar]]("bars"))) else ServiceClient.post("daily","getprices",Json.obj("symbols"->List(symbol).asJson,"start"->start.asJson,"end"->end.asJson)).flatMap(j=>IO.fromEither(j.hcursor.downField("series").get[List[DailyBar]](symbol)))
      bars=Aggregation.aggregate(source,frequency)
      _<-IO(require(bars.size<=5000,"单次查询最多5000根K线，请缩小日期区间"))
      expected=Map("2min"->2,"5min"->5).getOrElse(frequency,1)
    yield GetBarsResponse(symbol,frequency,if minute then "1min" else "1d",bars,start,end,if minute then bars.count(_.minutes<expected) else 0)
object GetBarsMessage:
  given Decoder[GetBarsMessage]=deriveDecoder
