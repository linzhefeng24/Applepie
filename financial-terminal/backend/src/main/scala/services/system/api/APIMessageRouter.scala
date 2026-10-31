package services.system.api
import cats.effect.IO
import io.circe.{Decoder, Encoder, Json}
import io.circe.syntax.*
import org.http4s.{HttpRoutes, Request, Response}
import org.http4s.circe.*
import org.http4s.dsl.io.*
import services.system.Database
object APIMessageRouter:
  def register[M <: APIMessage[A]: Decoder, A: Encoder](name: String): APIRegistration =
    APIRegistration(
      name.stripSuffix("Message").toLowerCase,
      json =>
        IO.fromEither(json.as[M].left.map(e => new IllegalArgumentException(e.getMessage)))
          .flatMap(message => Database.transaction(message.plan))
          .map(_.asJson)
    )
  def routes(service: String, entries: List[APIRegistration]): HttpRoutes[IO] = HttpRoutes.of[IO] {
    case GET -> Root / "api" / `service` / "openapi.json" => Ok(OpenApi.document(service, entries))
    case GET -> Root / "health" =>
      Database
        .transaction(c =>
          IO.blocking {
            val s = c.createStatement();
            try {
              val r = s.executeQuery("SELECT 1");
              try r.next()
              finally r.close()
            } finally s.close()
          }
        )
        .flatMap(_ => Ok(Json.obj("status" -> "ok".asJson, "service" -> service.asJson)))
    case request @ POST -> Root / "api" / `service` / name =>
      entries.find(_.name == name).fold(NotFound(Json.obj("error" -> "Unknown API".asJson))) {
        entry =>
          request.as[Json].flatMap(entry.execute).flatMap(Ok(_)).handleErrorWith {
            case e: IllegalArgumentException => BadRequest(Json.obj("error" -> e.getMessage.asJson))
            case e: org.http4s.InvalidMessageBodyFailure =>
              BadRequest(Json.obj("error" -> "Invalid JSON body".asJson))
            case e =>
              IO.println(
                s"[$service] ${e.getClass.getSimpleName}: ${e.getMessage}"
              ) *> InternalServerError(Json.obj("error" -> "服务处理失败，请检查服务日志或数据状态".asJson))
          }
      }
  }
