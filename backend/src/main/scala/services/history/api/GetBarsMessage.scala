package services.history.api
import cats.effect.IO
import io.circe.Decoder
import io.circe.generic.semiauto.*
import java.sql.Connection
import services.system.api.APIMessage
import services.history.utils.Validation
import services.history.tables.DailyBarTable.DailyBarTable
import services.history.tables.MinuteBarTable.MinuteBarTable
import services.history.objects.apiTypes.GetBarsResponse
final case class GetBarsMessage(symbol:String,start:String,end:String,frequency:String) extends APIMessage[GetBarsResponse]:
  def plan(connection: Connection): IO[GetBarsResponse]=for
    _ <- IO(Validation.dates(start,end))
    available <- ListFrequenciesMessage(symbol).plan(connection)
    option <- IO.fromOption(available.frequencies.find(f=>f.code==frequency&&f.available))(new IllegalArgumentException("该证券没有此频率的真实数据，或历史不足以显示年线"))
    minute=frequency.endsWith("min")
    bars <- if minute then MinuteBarTable.aggregate(connection,symbol,start,end,frequency) else DailyBarTable.aggregate(connection,symbol,start,end,frequency)
    _ <- IO(require(bars.size<=available.maxBars,"单次查询最多5000根K线，请缩小日期区间；数据不会被静默截断"))
    expected=Map("2min"->2,"5min"->5).getOrElse(frequency,1)
  yield GetBarsResponse(symbol,frequency,if minute then "1min" else "1d",bars,start,end,if minute then bars.count(_.minutes<expected) else 0)
object GetBarsMessage:
  given Decoder[GetBarsMessage]=deriveDecoder
