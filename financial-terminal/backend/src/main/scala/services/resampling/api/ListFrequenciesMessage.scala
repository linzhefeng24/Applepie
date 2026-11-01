package services.resampling.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.StatelessMessage
import services.system.http.ServiceClient
import services.resampling.objects.FrequencyOption
import services.resampling.objects.apiTypes.ListFrequenciesResponse
final case class ListFrequenciesMessage(symbol:String) extends StatelessMessage[services.resampling.objects.apiTypes.ListFrequenciesResponse]:
  def plan: IO[services.resampling.objects.apiTypes.ListFrequenciesResponse] =
    for
      daily<-ServiceClient.post("daily","getcoverage",Json.obj("symbol"->symbol.asJson))
      _<-IO(require(!daily.isNull,"证券不在已导入样本中"))
      minute<-ServiceClient.post("minute","getcoverage",Json.obj("symbol"->symbol.asJson))
      start=daily.hcursor.get[String]("start").fold(throw _,identity)
      end=daily.hcursor.get[String]("end").fold(throw _,identity)
      count=daily.hcursor.get[Long]("observations").fold(throw _,identity)
      years=java.time.LocalDate.parse(end).getYear-java.time.LocalDate.parse(start).getYear-1
      calendar=List(FrequencyOption("1y","年",years>=3,start,end,years),FrequencyOption("1mo","月",true,start,end,count),FrequencyOption("1d","日",true,start,end,count))
      minutes=List(("5min","5分钟"),("2min","2分钟"),("1min","1分钟")).map((code,label)=>FrequencyOption(code,label,!minute.isNull,minute.hcursor.get[String]("start").getOrElse(""),minute.hcursor.get[String]("end").getOrElse(""),minute.hcursor.get[Long]("observations").getOrElse(0)))
    yield ListFrequenciesResponse(symbol,calendar++minutes,5000,"原始时间戳无时区标记，不补造缺失分钟")
object ListFrequenciesMessage:
  given Decoder[ListFrequenciesMessage]=deriveDecoder
