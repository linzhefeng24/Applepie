package services.backtest.utils
import cats.effect.IO
import scala.concurrent.duration.*
import org.http4s.{Request, Method, Uri}
import org.http4s.client.Client
import org.http4s.ember.client.EmberClientBuilder
import org.http4s.circe.*
import io.circe.Json
private[backtest] object Remote:
  def post(url: String, body: Json): IO[Json] =
    EmberClientBuilder.default[IO].withTimeout(180.seconds).build.use { client =>
      client
        .run(Request[IO](method = Method.POST, uri = Uri.unsafeFromString(url)).withEntity(body))
        .use { response =>
          response.as[Json].flatMap { json =>
            if response.status.isSuccess then IO.pure(json)
            else
              IO.raiseError(
                new IllegalArgumentException(json.hcursor.get[String]("error").getOrElse("下游服务不可用"))
              )
          }
        }
    }
