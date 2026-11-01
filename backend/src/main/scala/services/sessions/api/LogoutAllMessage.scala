package services.sessions.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{APIMessage,HttpError}
import services.sessions.tables.SessionTable.SessionTable
import services.sessions.utils.SessionTokens
final case class LogoutAllMessage(userId:String) extends APIMessage[Json]:
  def plan(connection: Connection): IO[Json] =
    SessionTable.revoke(connection,userId,None,None).as(Json.obj("loggedOut"->true.asJson))
object LogoutAllMessage:
  given Decoder[LogoutAllMessage]=deriveDecoder
