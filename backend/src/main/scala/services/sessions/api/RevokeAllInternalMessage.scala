package services.sessions.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{APIMessage,HttpError}
import services.sessions.tables.SessionTable.SessionTable
import services.sessions.utils.SessionTokens
final case class RevokeAllInternalMessage(userId:String) extends APIMessage[Json]:
  def plan(connection: Connection): IO[Json] =
    SessionTable.revoke(connection,userId,None,None).as(Json.obj("revoked"->true.asJson))
object RevokeAllInternalMessage:
  given Decoder[RevokeAllInternalMessage]=deriveDecoder
