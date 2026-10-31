package services.market.api
import services.market.objects.apiTypes.ListStocksResponse
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import java.nio.file.{Files, Path}
import services.system.api.NoRequestMessage
import services.market.tables.StockTable.StockTable
final case class ListStocksMessage() extends NoRequestMessage[ListStocksResponse]:
  def plan(connection: Connection): IO[ListStocksResponse] =
    for
      stocks <- StockTable.list(connection)
      quotes <- services.market.tables.DailyBarTable.DailyBarTable.latest(connection)
      provenance <- IO
        .blocking(
          Files.readString(Path.of(sys.env.getOrElse("DATA_DIR", "data"), "provenance.json"))
        )
        .flatMap(s => IO.fromEither(io.circe.parser.parse(s)))
    yield ListStocksResponse(stocks, quotes, provenance)
object ListStocksMessage:
  given Decoder[ListStocksMessage] = deriveDecoder
