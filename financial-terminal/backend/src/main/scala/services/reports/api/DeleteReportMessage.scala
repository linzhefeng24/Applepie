package services.reports.api
import services.reports.objects.apiTypes.DeleteReportResponse
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import java.util.UUID
import services.system.api.APIMessage
import services.reports.tables.ReportTable.ReportTable
final case class DeleteReportMessage(userId:String,id: String) extends APIMessage[DeleteReportResponse]:
  def plan(connection: Connection): IO[DeleteReportResponse] =
    IO(UUID.fromString(id)).handleErrorWith(_ =>
      IO.raiseError(new IllegalArgumentException("无效报告 ID"))
    ) *> ReportTable.delete(connection, id,userId).as(DeleteReportResponse(true))
object DeleteReportMessage:
  given Decoder[DeleteReportMessage] = deriveDecoder
