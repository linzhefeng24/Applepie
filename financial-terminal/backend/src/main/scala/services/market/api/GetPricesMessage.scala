package services.market.api
import services.market.objects.apiTypes.GetPricesResponse
import cats.effect.IO
import cats.syntax.all.*
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.APIMessage
import services.market.tables.StockTable.StockTable
import services.market.tables.DailyBarTable.DailyBarTable
import services.market.utils.Validation
final case class GetPricesMessage(symbols: List[String], start: String, end: String)
    extends APIMessage[GetPricesResponse]:
  def plan(connection: Connection): IO[GetPricesResponse] =
    for
      _ <- IO {
        Validation.dates(start, end);
        require(
          symbols.nonEmpty && symbols.size <= 10 && symbols.distinct.size == symbols.size,
          "选择 1–10 个不重复标的"
        )
      }
      stocks <- StockTable.list(connection)
      _ <- IO(require(symbols.forall(s => stocks.exists(_.symbol == s)), "存在未导入的标的"))
      series <- symbols.traverse(s =>
        DailyBarTable.find(connection, s, start, end).map(b => s -> b)
      )
    yield GetPricesResponse(series.toMap)
object GetPricesMessage:
  given Decoder[GetPricesMessage] = deriveDecoder
