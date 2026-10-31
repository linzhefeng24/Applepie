package services.statistics.api
import services.statistics.objects.apiTypes.GetStockResponse
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.APIMessage
import services.market.tables.StockTable.StockTable
import services.history.tables.DailyBarTable.DailyBarTable
import services.statistics.utils.{Validation, Statistics}
final case class GetStockMessage(symbol: String, start: String, end: String)
    extends APIMessage[GetStockResponse]:
  def plan(connection: Connection): IO[GetStockResponse] =
    for
      _ <- IO(Validation.dates(start, end))
      stocks <- StockTable.list(connection)
      stock <- IO
        .fromOption(stocks.find(_.symbol == symbol))(new IllegalArgumentException("股票不在已导入样本中"))
      bars <- DailyBarTable.find(connection, symbol, start, end)
    yield GetStockResponse(stock, bars, Statistics.summary(bars), Statistics.annual(bars))
object GetStockMessage:
  given Decoder[GetStockMessage] = deriveDecoder
