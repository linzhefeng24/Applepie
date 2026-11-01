package services.authorization.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{ComposedMessage,HttpError}
import services.authorization.tables.AccessTable.AccessTable
import services.authorization.utils.Permissions
import services.system.http.ServiceClient
import services.system.Database
final case class ResolveIdentityMessage(userId:String,credentialsVersion:Int) extends ComposedMessage[Json]:
  def plan: IO[Json] =
    for
      user<-ServiceClient.post("accounts","finduser",Json.obj("userId"->userId.asJson),true)
      _<-IO.raiseWhen(!user.hcursor.get[Int]("credentialsVersion").contains(credentialsVersion))(HttpError(401,"密码已更改，请重新登录"))
      access<-Database.transaction(c=>AccessTable.get(c,userId)).flatMap(a=>IO.fromOption(a)(HttpError(403,"账户尚未完成权限配置")))
      _<-IO.raiseWhen(!access._2)(HttpError(403,"账户已被停用"))
    yield Json.obj("id"->userId.asJson,"username"->user.hcursor.get[String]("username").getOrElse("").asJson,"displayName"->user.hcursor.get[String]("displayName").getOrElse("").asJson,"role"->access._1.asJson,"enabled"->access._2.asJson,"permissions"->Permissions.forRole(access._1).asJson)
object ResolveIdentityMessage:
  given Decoder[ResolveIdentityMessage]=deriveDecoder
