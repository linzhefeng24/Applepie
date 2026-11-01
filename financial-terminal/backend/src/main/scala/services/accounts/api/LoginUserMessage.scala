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
final case class LoginUserMessage(username:String,password:String) extends ComposedMessage[Json]:
  def plan: IO[Json] =
    for
      name<-IO(username.trim.toLowerCase(java.util.Locale.ROOT))
      _<-IO(LoginLimiter.check(name))
      user<-Database.transaction(c=>UserTable.byName(c,name))
      valid<-IO.blocking(PasswordHasher.verify(password,user.map(_.passwordHash)))
      _<-IO.raiseWhen(!valid)(HttpError(401,"账号或密码不正确"))
      result<-AccountWorkflow.start(user.get)
      _<-IO(LoginLimiter.clear(name))
    yield result
object LoginUserMessage:
  given Decoder[LoginUserMessage]=deriveDecoder
