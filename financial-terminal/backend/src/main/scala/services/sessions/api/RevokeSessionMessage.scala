package services.sessions.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{APIMessage,HttpError}
import services.sessions.tables.SessionTable.SessionTable
import services.sessions.utils.SessionTokens
final case class RevokeSessionMessage(userId:String,sessionId:String) extends APIMessage[Json]:
  def plan(connection: Connection): IO[Json] =
    IO(java.util.UUID.fromString(sessionId)) *> SessionTable.revoke(connection,userId,Some(sessionId),None).as(Json.obj("revoked"->true.asJson))
object RevokeSessionMessage:
  given Decoder[RevokeSessionMessage]=deriveDecoder
