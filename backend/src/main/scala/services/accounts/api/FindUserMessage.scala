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
final case class FindUserMessage(userId:String) extends ComposedMessage[Json]:
  def plan: IO[Json] =
    Database.transaction(c=>UserTable.byId(c,userId)).flatMap(user=>IO.fromOption(user)(HttpError(401,"账户不存在"))).map(AccountWorkflow.publicRecord)
object FindUserMessage:
  given Decoder[FindUserMessage]=deriveDecoder
