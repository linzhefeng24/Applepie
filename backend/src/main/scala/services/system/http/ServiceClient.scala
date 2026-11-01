package services.system.http
import cats.effect.{IO,Resource}
import io.circe.Json
import org.http4s.{Request,Method,Uri,Header}
import org.http4s.client.Client
import org.http4s.ember.client.EmberClientBuilder
import org.http4s.circe.*
import org.typelevel.ci.CIString
import scala.concurrent.duration.*
import java.util.concurrent.atomic.AtomicReference
import services.system.api.HttpError
object ServiceClient:
  private val client=new AtomicReference[Client[IO]]()
  val resource:Resource[IO,Unit]=EmberClientBuilder.default[IO].withTimeout(180.seconds).build.evalMap(c=>IO(client.set(c))).onFinalize(IO(client.set(null)))
  def post(service:String,api:String,body:Json,internal:Boolean=false):IO[Json]=
    val base=sys.env.getOrElse(service.toUpperCase+"_URL",throw new IllegalStateException(s"Missing service URL: $service"))
    val path=if internal then s"/internal/$service/$api" else s"/api/$service/$api"
    postUrl(base+path,body)
  def postUrl(url:String,body:Json):IO[Json]=IO.defer {
    val c=Option(client.get()).getOrElse(throw new IllegalStateException("HTTP client is not initialized"))
    val request=Request[IO](Method.POST,Uri.unsafeFromString(url)).withEntity(body).putHeaders(
      Header.Raw(CIString("X-Service-Name"),sys.env.getOrElse("SERVICE","")),
      Header.Raw(CIString("X-Internal-Token"),sys.env.getOrElse("INTERNAL_SERVICE_TOKEN","")))
    c.run(request).use { response=>response.as[Json].flatMap { result=>
      if response.status.isSuccess then IO.pure(result)
      else IO.raiseError(HttpError(if response.status.code<500 then response.status.code else 503,result.hcursor.get[String]("error").getOrElse("依赖服务暂不可用")))
    }}.handleErrorWith {
      case error:HttpError=>IO.raiseError(error)
      case _=>IO.raiseError(HttpError(503,"依赖服务连接失败，请稍后重试"))
    }
  }
