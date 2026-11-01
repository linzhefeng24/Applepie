package services.system.api
import cats.effect.IO
import cats.syntax.all.*
import io.circe.{Decoder,Encoder,Json}
import io.circe.syntax.*
import io.circe.parser.parse
import org.http4s.{HttpRoutes,Request,Response,Status,Header}
import org.http4s.dsl.io.*
import org.http4s.circe.*
import org.typelevel.ci.CIString
import services.system.Database
import services.system.security.{RequestIdentity,ServiceTrust}
object APIMessageRouter:
  def register[M <: APIMessage[A]:Decoder,A:Encoder](name:String,permission:String="data:read",ownerBound:Boolean=false,withSession:Boolean=false,issueCookie:Boolean=false,clearCookie:Boolean=false):APIRegistration=
    APIRegistration(name.stripSuffix("Message").toLowerCase,json=>IO.fromEither(json.as[M].left.map(e=>HttpError(400,e.getMessage))).flatMap(_.execute).map(_.asJson),permission,ownerBound,withSession,issueCookie,clearCookie)
  def registerInternal[M <: APIMessage[A]:Decoder,A:Encoder](name:String,callers:Set[String]=Set.empty):APIRegistration=register[M,A](name).copy(internalOnly=true,callers=callers)
  private def payload(request:Request[IO]):IO[Json]=for
    _<-IO.raiseWhen(!request.headers.get(CIString("Content-Type")).exists(_.head.value.toLowerCase.startsWith("application/json")))(HttpError(415,"请求必须使用 application/json"))
    bytes<-request.body.take(8000001).compile.to(Array)
    _<-IO.raiseWhen(bytes.length>8000000)(HttpError(413,"请求体超过上限"))
    json<-IO.fromEither(parse(new String(bytes,java.nio.charset.StandardCharsets.UTF_8)).left.map(_=>HttpError(400,"JSON格式无效")))
  yield json
  private def execute(request:Request[IO],entry:APIRegistration,internal:Boolean):IO[Response[IO]]=for
    _<-RequestIdentity.validateOrigin(request)
    body<-payload(request)
    trusted=ServiceTrust.caller(request)
    _<-IO.raiseWhen(entry.internalOnly!=internal)(HttpError(404,"Unknown API"))
    _<-IO.raiseWhen(internal&&(!trusted.exists(c=>entry.callers.isEmpty||entry.callers.contains(c))))(HttpError(403,"内部服务凭据无效"))
    _<-IO.raiseWhen(!internal&&body.asObject.exists(o=>List("userId","role","identity","sessionToken").exists(o.contains)))(HttpError(400,"身份字段由服务端解析，不能由请求指定"))
    bypass=internal||entry.permission=="public"||(trusted.nonEmpty&&entry.permission=="data:read")
    identity<-if bypass then IO.pure(Json.obj()) else RequestIdentity.resolve(request,entry.permission)
    prepared=if entry.ownerBound then body.deepMerge(Json.obj("userId"->identity.hcursor.get[String]("id").getOrElse(throw HttpError(401,"身份无效")).asJson)) else body
    withToken=if entry.withSession then prepared.deepMerge(Json.obj("sessionToken"->RequestIdentity.token(request).getOrElse("").asJson)) else prepared
    result<-entry.execute(withToken)
    response<-Ok(if entry.issueCookie then result.mapObject(_.remove("sessionToken")) else result)
    cookie=if entry.clearCookie then Some(s"${RequestIdentity.cookieName}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0") else if entry.issueCookie then Some(s"${RequestIdentity.cookieName}=${result.hcursor.get[String]("sessionToken").getOrElse(throw HttpError(500,"会话创建失败"))}; Path=/; HttpOnly; SameSite=Strict; Max-Age=43200${if sys.env.getOrElse("COOKIE_SECURE","false")=="true" then "; Secure" else ""}") else None
  yield cookie.fold(response)(value=>response.putHeaders(Header.Raw(CIString("Set-Cookie"),value)))
  private def errors(io:IO[Response[IO]]):IO[Response[IO]]=io.handleErrorWith {
    case e:HttpError=>Response[IO](Status.fromInt(e.status).getOrElse(Status.InternalServerError)).withEntity(Json.obj("error"->e.publicMessage.asJson)).pure[IO]
    case e:IllegalArgumentException=>BadRequest(Json.obj("error"->Option(e.getMessage).getOrElse("输入无效").asJson))
    case e=>IO.println(s"Service request failed: ${e.getClass.getSimpleName}") *> InternalServerError(Json.obj("error"->"服务暂不可用，请稍后重试".asJson))
  }
  def routes(service:String,entries:List[APIRegistration]):HttpRoutes[IO]=HttpRoutes.of[IO] {
    case GET -> Root / "health"=>errors(Database.ping *> Ok(Json.obj("status"->"ok".asJson,"service"->service.asJson)))
    case GET -> Root / "api" / `service` / "openapi.json"=>Ok(OpenApi.document(service,entries.filterNot(_.internalOnly)))
    case request @ POST -> Root / "api" / `service` / name=>entries.find(e=>e.name==name&& !e.internalOnly).fold(NotFound(Json.obj("error"->"Unknown API".asJson)))(entry=>errors(execute(request,entry,false)))
    case request @ POST -> Root / "internal" / `service` / name=>entries.find(e=>e.name==name&&e.internalOnly).fold(NotFound(Json.obj("error"->"Unknown API".asJson)))(entry=>errors(execute(request,entry,true)))
  }
