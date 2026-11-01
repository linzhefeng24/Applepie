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
final case class UpdateProfileMessage(userId:String,displayName:String) extends ComposedMessage[Json]:
  def plan: IO[Json] =
    IO(require(displayName.trim.nonEmpty&&displayName.length<=64,"显示名称需为1–64字")) *> Database.transaction(c=>UserTable.updateDisplay(c,userId,displayName.trim)) *> GetCurrentUserMessage(userId).plan
object UpdateProfileMessage:
  given Decoder[UpdateProfileMessage]=deriveDecoder
