package services.optimization.api
import cats.effect.IO
import io.circe.{Decoder, Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.StatelessMessage
import services.optimization.objects.AnalysisParameters
import services.optimization.utils.Remote
final case class RunAnalysisMessage(parameters: AnalysisParameters) extends StatelessMessage[Json]:
  def plan: IO[Json] =
    for
      _ <- IO {
        require(parameters.symbols.size >= 2 && parameters.symbols.size <= 10, "选择 2–10 个标的");
        require(
          parameters.maxWeight > 0 && parameters.maxWeight <= 1 && parameters.maxWeight * parameters.symbols.size >= 1 - 1e-9,
          "单股上限无法满足权重和为 1"
        )
      }
      prices <- Remote.post(
        sys.env("DAILY_URL") + "/api/daily/getprices",
        Json.obj(
          "symbols" -> parameters.symbols.asJson,
          "start" -> parameters.start.asJson,
          "end" -> parameters.end.asJson
        )
      )
      result <- Remote.post(
        sys.env("QUANT_OPTIMIZER_URL") + "/analyze",
        Json.obj(
          "parameters" -> parameters.asJson,
          "series" -> prices.hcursor.downField("series").focus.getOrElse(Json.obj())
        )
      )
    yield result
object RunAnalysisMessage:
  given Decoder[RunAnalysisMessage] = deriveDecoder
