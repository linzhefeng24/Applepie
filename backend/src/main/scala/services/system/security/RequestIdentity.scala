package services.system.security
import cats.effect.IO
import io.circe.Json
import io.circe.syntax.*
import org.http4s.Request
import org.typelevel.ci.CIString
import services.system.http.ServiceClient
import services.system.api.HttpError
object RequestIdentity:
  val cookieName="aperture_session"
  def token(request:Request[IO]):Option[String]=
    request.headers.get(CIString("Authorization")).map(_.head.value).filter(_.startsWith("Bearer ")).map(_.drop(7)).orElse(
      request.cookies.find(_.name==cookieName).map(_.content))
  def resolve(request:Request[IO],permission:String):IO[Json]=for
    raw<-IO.fromOption(token(request))(HttpError(401,"请先登录"))
    session<-ServiceClient.post("sessions","validatesession",Json.obj("token"->raw.asJson),true)
    userId<-IO.fromEither(session.hcursor.get[String]("userId").left.map(_=>HttpError(401,"会话无效")))
    version<-IO.fromEither(session.hcursor.get[Int]("credentialsVersion").left.map(_=>HttpError(401,"会话无效")))
    identity<-ServiceClient.post("authorization","resolveidentity",Json.obj("userId"->userId.asJson,"credentialsVersion"->version.asJson),true)
    permissions<-IO.fromEither(identity.hcursor.get[List[String]]("permissions").left.map(_=>HttpError(403,"无权执行此操作")))
    _<-IO.raiseWhen(!permissions.contains(permission))(HttpError(403,"当前账户没有此操作权限"))
  yield identity
  def validateOrigin(request:Request[IO]):IO[Unit]=IO {
    request.headers.get(CIString("Origin")).foreach { value=>
      val origin=value.head.value
      val ports=List(sys.env.getOrElse("FRONTEND_PORT","4173"),sys.env.getOrElse("DEV_PORT","5173"))
      val local=ports.flatMap(p=>List(s"http://127.0.0.1:$p",s"http://localhost:$p"))
      val explicit=sys.env.getOrElse("ALLOWED_ORIGINS","").split(',').filter(_.nonEmpty).toList
      if !(local++explicit).contains(origin) then throw HttpError(403,"请求来源不被允许")
    }
  }
