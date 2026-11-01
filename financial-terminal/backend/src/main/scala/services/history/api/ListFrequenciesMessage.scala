package services.history.api
import cats.effect.IO
import io.circe.Decoder
import io.circe.generic.semiauto.*
import java.sql.Connection
import java.time.LocalDate
import services.system.api.APIMessage
import services.market.tables.StockTable.StockTable
import services.history.tables.MinuteBarTable.MinuteBarTable
import services.history.objects.FrequencyOption
import services.history.objects.apiTypes.ListFrequenciesResponse
final case class ListFrequenciesMessage(symbol:String) extends APIMessage[ListFrequenciesResponse]:
  def plan(connection: Connection): IO[ListFrequenciesResponse]=for
    stocks <- StockTable.list(connection)
    stock <- IO.fromOption(stocks.find(_.symbol==symbol))(new IllegalArgumentException("证券不在已导入样本中"))
    minute <- MinuteBarTable.bounds(connection,symbol)
    completeYears=LocalDate.parse(stock.lastDate).getYear-LocalDate.parse(stock.firstDate).getYear-1
    calendar=List(FrequencyOption("1y","年",completeYears>=3,stock.firstDate,stock.lastDate,completeYears),FrequencyOption("1mo","月",true,stock.firstDate,stock.lastDate,stock.sessions),FrequencyOption("1d","日",true,stock.firstDate,stock.lastDate,stock.sessions))
    minutes=List(("5min","5分钟"),("2min","2分钟"),("1min","1分钟")).map((code,label)=>FrequencyOption(code,label,minute.nonEmpty,minute.map(_._1).getOrElse(""),minute.map(_._2).getOrElse(""),minute.map(_._3).getOrElse(0L)))
  yield ListFrequenciesResponse(symbol,calendar++minutes,5000,"源时间戳未标注时区；按原始时间和自然日分桶，不推测交易所时区。")
object ListFrequenciesMessage:
  given Decoder[ListFrequenciesMessage]=deriveDecoder
