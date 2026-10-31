package services.system.api
import io.circe.Json
import io.circe.syntax.*
/** Request schemas and API discovery are platform concerns, separate from business plans. */
object OpenApi:
  private def scalar(kind: String): Json = Json.obj("type" -> kind.asJson)
  private val text = scalar("string")
  private val date = Json.obj("type" -> "string".asJson, "format" -> "date".asJson)
  private val number = scalar("number")
  private def fields(values: (String, Json)*): Json =
    val base = Json.obj("type" -> "object".asJson, "properties" -> Json.obj(values*))
    if values.isEmpty then base else base.deepMerge(Json.obj("required" -> values.map(_._1).asJson))
  private def symbols(maximum: Int, minimum: Int = 1): Json = Json.obj("type" -> "array".asJson, "items" -> text,
    "minItems" -> minimum.asJson, "maxItems" -> maximum.asJson, "uniqueItems" -> true.asJson)
  private def bounded(kind: String, minimum: Double, maximum: Double): Json =
    Json.obj("type" -> kind.asJson, "minimum" -> minimum.asJson, "maximum" -> maximum.asJson)
  private val parameters = fields("symbols" -> symbols(10, 2), "start" -> date, "end" -> date,
    "maxWeight" -> bounded("number", 0, 1), "riskAversion" -> bounded("number", 0, 100), "skewPreference" -> bounded("number", 0, 20),
    "kurtosisAversion" -> bounded("number", 0, 20), "lookback" -> bounded("integer", 60, 504),
    "rebalance" -> bounded("integer", 5, 126), "costBps" -> bounded("number", 0, 100),
    "model" -> Json.obj("type" -> "string".asJson,
      "enum" -> List("equal", "minvariance", "meanvariance", "mvsk", "riskparity").asJson))
  private val schemas = Map(
    "liststocks" -> fields(), "listwatchlist" -> fields(), "listreports" -> fields(),
    "getstock" -> fields("symbol" -> text, "start" -> date, "end" -> date),
    "getprices" -> fields("symbols" -> symbols(10), "start" -> date, "end" -> date),
    "setwatchlist" -> fields("symbol" -> text, "selected" -> scalar("boolean")),
    "deletereport" -> fields("id" -> text),
    "savereport" -> fields("title" -> text, "kind" -> Json.obj("type" -> "string".asJson,
      "enum" -> List("analysis", "backtest").asJson), "parameters" -> scalar("object"), "result" -> scalar("object")),
    "runanalysis" -> fields("parameters" -> parameters),
    "runbacktest" -> fields("parameters" -> parameters)
  )
  def document(service: String, entries: List[APIRegistration]): Json = Json.obj(
    "openapi" -> "3.0.3".asJson,
    "info" -> Json.obj("title" -> s"APERTURE $service API".asJson, "version" -> "2.0.0".asJson,
      "description" -> "Local historical research service. POST JSON; dates are inclusive. No live order execution.".asJson),
    "servers" -> Json.arr(Json.obj("url" -> "/".asJson)),
    "paths" -> Json.obj(entries.map { registration =>
      s"/api/$service/${registration.name}" -> Json.obj("post" -> Json.obj(
        "operationId" -> s"${service}_${registration.name}".asJson,
        "requestBody" -> Json.obj("required" -> true.asJson, "content" -> Json.obj(
          "application/json" -> Json.obj("schema" -> schemas.getOrElse(registration.name, fields())))),
        "responses" -> Json.obj(
          "200" -> Json.obj("description" -> "Successful typed message response; see API reference for response fields.".asJson,
            "content" -> Json.obj("application/json" -> Json.obj("schema" -> scalar("object")))),
          "400" -> Json.obj("description" -> "Invalid JSON, dates, symbol or constraints. JSON error field.".asJson),
          "500" -> Json.obj("description" -> "Service or dependency failure. JSON error field; details stay in local logs.".asJson)
        )
      ))
    }*)
  )
