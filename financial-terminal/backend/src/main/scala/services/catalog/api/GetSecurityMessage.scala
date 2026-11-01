package services.catalog.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.APIMessage
import services.catalog.tables.StockTable.StockTable
final case class GetSecurityMessage(symbol:String) extends APIMessage[services.catalog.objects.Stock]:
  def plan(connection: Connection): IO[services.catalog.objects.Stock] =
    for
      stocks<-StockTable.list(connection)
      stock<-IO.fromOption(stocks.find(_.symbol==symbol))(new IllegalArgumentException("证券不在已导入样本中"))
    yield stock
object GetSecurityMessage:
  given Decoder[GetSecurityMessage]=deriveDecoder
