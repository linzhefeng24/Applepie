package services.authorization.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{ComposedMessage,HttpError}
import services.authorization.tables.AccessTable.AccessTable
import services.authorization.utils.Permissions
import services.system.http.ServiceClient
import services.system.Database
final case class EnsureAccessMessage(userId:String) extends ComposedMessage[Json]:
  def plan: IO[Json] =
    for
      user<-ServiceClient.post("accounts","finduser",Json.obj("userId"->userId.asJson),true)
      bootstrap=user.hcursor.get[Boolean]("bootstrap").getOrElse(false)
      _<-Database.transaction(c=>AccessTable.ensure(c,userId,bootstrap))
    yield Json.obj("ready"->true.asJson)
object EnsureAccessMessage:
  given Decoder[EnsureAccessMessage]=deriveDecoder
