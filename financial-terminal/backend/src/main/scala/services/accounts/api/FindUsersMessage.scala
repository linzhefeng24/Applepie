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
final case class FindUsersMessage() extends ComposedMessage[Json]:
  def plan: IO[Json] =
    Database.transaction(UserTable.list).map(users=>users.map(AccountWorkflow.publicRecord).asJson)
object FindUsersMessage:
  given Decoder[FindUsersMessage]=deriveDecoder
