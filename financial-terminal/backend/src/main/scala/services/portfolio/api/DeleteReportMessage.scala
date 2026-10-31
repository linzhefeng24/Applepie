package services.portfolio.api
import services.portfolio.objects.apiTypes.DeleteReportResponse
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import java.util.UUID
import services.system.api.APIMessage
import services.portfolio.tables.ReportTable.ReportTable
final case class DeleteReportMessage(id: String) extends APIMessage[DeleteReportResponse]:
  def plan(connection: Connection): IO[DeleteReportResponse] =
    IO(UUID.fromString(id)).handleErrorWith(_ =>
      IO.raiseError(new IllegalArgumentException("无效报告 ID"))
    ) *> ReportTable.delete(connection, id).as(DeleteReportResponse(true))
object DeleteReportMessage:
  given Decoder[DeleteReportMessage] = deriveDecoder
