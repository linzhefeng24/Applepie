package services.system
import cats.effect.IO
import cats.syntax.all.*
import com.comcast.ip4s.{Host,Port}
import org.http4s.ember.server.EmberServerBuilder
import services.system.api.{APIMessageRouter,APIRegistration}
import services.system.http.ServiceClient
object ServiceServer:
  def run(service:String,entries:List[APIRegistration],initialize:IO[Unit]):IO[Unit]=
    (ServiceClient.resource *> Database.resource).use { _=> initialize *> EmberServerBuilder.default[IO]
      .withHost(Host.fromString(sys.env.getOrElse("SERVICE_HOST","127.0.0.1")).get)
      .withPort(Port.fromInt(sys.env("HTTP_PORT").toInt).get)
      .withHttpApp(APIMessageRouter.routes(service,entries).orNotFound).build
      .use(_=>IO.println(s"$service ready on ${sys.env("HTTP_PORT")}") *> IO.never)
    }
