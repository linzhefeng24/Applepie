package services.accounts.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{ComposedMessage,HttpError}
import services.system.Database
import services.accounts.tables.UserTable.UserTable
import services.accounts.utils.{PasswordHasher,AccountWorkflow,LoginLimiter}
import services.system.http.ServiceClient
final case class ChangePasswordMessage(userId:String,currentPassword:String,newPassword:String) extends ComposedMessage[Json]:
  def plan: IO[Json] =
    for
      user<-Database.transaction(c=>UserTable.byId(c,userId)).flatMap(u=>IO.fromOption(u)(HttpError(401,"账户不存在")))
      valid<-IO.blocking(PasswordHasher.verify(currentPassword,Some(user.passwordHash)))
      _<-IO.raiseWhen(!valid)(HttpError(401,"原密码不正确"))
      digest<-IO.blocking(PasswordHasher.hash(newPassword))
      _<-Database.transaction(c=>UserTable.changePassword(c,user.id,user.credentialsVersion,digest))
      _<-ServiceClient.post("sessions","revokeallinternal",Json.obj("userId"->user.id.asJson),true).attempt
    yield Json.obj("changed"->true.asJson)
object ChangePasswordMessage:
  given Decoder[ChangePasswordMessage]=deriveDecoder
