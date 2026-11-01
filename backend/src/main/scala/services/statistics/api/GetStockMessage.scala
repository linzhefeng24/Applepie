package services.statistics.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.StatelessMessage
import services.system.http.ServiceClient
import services.catalog.objects.Stock
import services.daily.objects.DailyBar
import services.statistics.objects.apiTypes.GetStockResponse
final case class GetStockMessage(symbol:String,start:String,end:String) extends StatelessMessage[services.statistics.objects.apiTypes.GetStockResponse]:
  def plan: IO[services.statistics.objects.apiTypes.GetStockResponse] =
    for
      stockJson<-ServiceClient.post("catalog","getsecurity",Json.obj("symbol"->symbol.asJson))
      stock<-IO.fromEither(stockJson.as[Stock])
      prices<-ServiceClient.post("daily","getprices",Json.obj("symbols"->List(symbol).asJson,"start"->start.asJson,"end"->end.asJson))
      bars<-IO.fromEither(prices.hcursor.downField("series").get[List[DailyBar]](symbol))
      input=Json.obj("symbol"->symbol.asJson,"start"->start.asJson,"end"->end.asJson)
      performance<-ServiceClient.post("performance","getperformance",input)
      risk<-ServiceClient.post("risk","getrisk",input)
      annual<-ServiceClient.post("annual","getannual",input)
    yield GetStockResponse(stock,bars,performance.deepMerge(risk),annual)
object GetStockMessage:
  given Decoder[GetStockMessage]=deriveDecoder
