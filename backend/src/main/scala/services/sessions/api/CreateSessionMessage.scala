package services.sessions.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.{ComposedMessage,HttpError}
import services.sessions.tables.SessionTable.SessionTable
import services.sessions.utils.SessionTokens
import services.system.Database
import services.system.http.ServiceClient
final case class CreateSessionMessage(userId:String,credentialsVersion:Int) extends ComposedMessage[Json]:
  def plan: IO[Json] =
    for
      user<-ServiceClient.post("accounts","finduser",Json.obj("userId"->userId.asJson),true)
      _<-IO.raiseWhen(!user.hcursor.get[Int]("credentialsVersion").contains(credentialsVersion))(HttpError(401,"凭据已更新，请重新登录"))
      token<-IO(SessionTokens.create())
      id<-IO(java.util.UUID.randomUUID().toString)
      expires<-IO(java.time.Instant.now().plusSeconds(43200).toString)
      _<-Database.transaction(c=>SessionTable.create(c,id,userId,SessionTokens.hash(token),credentialsVersion,expires))
    yield Json.obj("sessionToken"->token.asJson,"expiresAt"->expires.asJson)
object CreateSessionMessage:
  given Decoder[CreateSessionMessage]=deriveDecoder
