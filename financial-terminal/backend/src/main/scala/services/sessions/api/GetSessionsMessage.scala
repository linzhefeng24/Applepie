package services.sessions.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{APIMessage,HttpError}
import services.sessions.tables.SessionTable.SessionTable
import services.sessions.utils.SessionTokens
final case class GetSessionsMessage(userId:String,sessionToken:String) extends APIMessage[Json]:
  def plan(connection: Connection): IO[Json] =
    SessionTable.list(connection,userId,SessionTokens.hash(sessionToken)).map(items=>Json.obj("sessions"->items))
object GetSessionsMessage:
  given Decoder[GetSessionsMessage]=deriveDecoder
