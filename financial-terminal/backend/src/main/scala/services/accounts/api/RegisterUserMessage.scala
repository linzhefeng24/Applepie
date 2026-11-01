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
final case class RegisterUserMessage(username:String,password:String,displayName:String) extends ComposedMessage[Json]:
  def plan: IO[Json] =
    for
      name<-IO {val value=username.trim.toLowerCase(java.util.Locale.ROOT);require(value.matches("[a-z0-9_]{3,32}"),"用户名需为3–32位字母、数字或下划线");require(displayName.trim.nonEmpty&&displayName.length<=64,"显示名称需为1–64字");value}
      digest<-IO.blocking(PasswordHasher.hash(password))
      id<-IO(java.util.UUID.randomUUID().toString)
      user<-Database.transaction(c=>UserTable.create(c,id,name,displayName.trim,digest))
      response<-AccountWorkflow.start(user).handleErrorWith {case e:HttpError if e.status>=500=>IO.raiseError(HttpError(503,"账户已创建，依赖服务暂不可用，请稍后使用相同账号登录"));case e=>IO.raiseError(e)}
    yield response
object RegisterUserMessage:
  given Decoder[RegisterUserMessage]=deriveDecoder
