package services.minute.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.APIMessage
import services.minute.tables.MinuteBarTable.MinuteBarTable
import services.minute.utils.Validation
final case class GetMinutePricesMessage(symbol:String,start:String,end:String) extends APIMessage[Json]:
  def plan(connection: Connection): IO[Json] =
    for
      _<-IO(Validation.dates(start,end))
      rows<-MinuteBarTable.raw(connection,symbol,start,end)
      _<-IO(require(rows.size<=50000,"原始分钟记录超过50000条，请缩小区间"))
    yield Json.obj("bars"->rows.asJson)
object GetMinutePricesMessage:
  given Decoder[GetMinutePricesMessage]=deriveDecoder
