package services.authorization.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{APIMessage,HttpError}
import services.authorization.tables.AccessTable.AccessTable
import services.authorization.utils.Permissions
import services.system.http.ServiceClient
import services.system.Database
final case class SetAccessMessage(targetUserId:String,newRole:String,enabled:Boolean) extends APIMessage[Json]:
  def plan(connection: Connection): IO[Json] =
    IO(java.util.UUID.fromString(targetUserId)) *> AccessTable.set(connection,targetUserId,newRole,enabled).as(Json.obj("updated"->true.asJson))
object SetAccessMessage:
  given Decoder[SetAccessMessage]=deriveDecoder
