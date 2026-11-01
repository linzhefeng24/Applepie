package services.daily.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.APIMessage
import services.daily.tables.DailyBarTable.DailyBarTable
final case class GetTailBarsMessage() extends APIMessage[services.daily.objects.apiTypes.GetPricesResponse]:
  def plan(connection: Connection): IO[services.daily.objects.apiTypes.GetPricesResponse] =
    DailyBarTable.tails(connection).map(services.daily.objects.apiTypes.GetPricesResponse.apply)
object GetTailBarsMessage:
  given Decoder[GetTailBarsMessage]=deriveDecoder
