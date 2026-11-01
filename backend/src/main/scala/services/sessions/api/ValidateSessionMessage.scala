package services.sessions.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{APIMessage,HttpError}
import services.sessions.tables.SessionTable.SessionTable
import services.sessions.utils.SessionTokens
final case class ValidateSessionMessage(token:String) extends APIMessage[Json]:
  def plan(connection: Connection): IO[Json] =
    IO.raiseWhen(token.length<32||token.length>256)(HttpError(401,"会话无效或已过期")) *> SessionTable.validate(connection,SessionTokens.hash(token)).flatMap(value=>IO.fromOption(value)(HttpError(401,"会话无效或已过期")))
object ValidateSessionMessage:
  given Decoder[ValidateSessionMessage]=deriveDecoder
