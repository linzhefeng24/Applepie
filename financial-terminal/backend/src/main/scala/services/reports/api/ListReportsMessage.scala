package services.reports.api
import services.reports.objects.apiTypes.ListReportsResponse
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.NoRequestMessage
import services.reports.tables.ReportTable.ReportTable
final case class ListReportsMessage(userId:String) extends NoRequestMessage[ListReportsResponse]:
  def plan(connection: Connection): IO[ListReportsResponse] =
    ReportTable.list(connection,userId).map(xs => ListReportsResponse(xs))
object ListReportsMessage:
  given Decoder[ListReportsMessage] = deriveDecoder
