package services.reports.api
import services.reports.objects.apiTypes.SaveReportResponse
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import java.util.UUID
import services.system.api.APIMessage
import services.reports.tables.ReportTable.ReportTable
final case class SaveReportMessage(userId:String,title: String, kind: String, parameters: Json, result: Json)
    extends APIMessage[SaveReportResponse]:
  def plan(connection: Connection): IO[SaveReportResponse] =
    for
      _ <- IO {
        require(title.trim.nonEmpty && title.length <= 160, "报告名称需为 1–160 字");
        require(Set("analysis", "backtest").contains(kind), "无效报告类型");
        require(result.noSpaces.length <= 2000000, "报告超过大小限制")
        require(parameters.as[services.optimization.objects.AnalysisParameters].isRight, "报告参数格式无效")
        require(result.hcursor.get[List[String]]("symbols").exists(_.nonEmpty), "报告缺少标的")
        require(
          result.hcursor.get[String]("start").isRight && result.hcursor.get[String]("end").isRight,
          "报告缺少日期"
        )
        require(
          result.hcursor
            .downField(if kind == "analysis" then "models" else "results")
            .focus
            .exists(_.isArray),
          "报告结果格式无效"
        )
      }
      id <- IO(UUID.randomUUID().toString)
      _ <- ReportTable.insert(connection, id,userId, title.trim, kind, parameters, result)
    yield SaveReportResponse(id)
object SaveReportMessage:
  given Decoder[SaveReportMessage] = deriveDecoder
