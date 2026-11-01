package services.accounts.utils
import cats.effect.IO
import io.circe.Json
import io.circe.syntax.*
import services.accounts.objects.StoredUser
import services.system.http.ServiceClient
private[accounts] object AccountWorkflow:
  def publicRecord(user:StoredUser):Json=Json.obj("id"->user.id.asJson,"username"->user.username.asJson,"displayName"->user.displayName.asJson,"credentialsVersion"->user.credentialsVersion.asJson,"bootstrap"->user.bootstrap.asJson)
  def identity(user:StoredUser):IO[Json]=ServiceClient.post("authorization","resolveidentity",Json.obj("userId"->user.id.asJson,"credentialsVersion"->user.credentialsVersion.asJson),true)
  def start(user:StoredUser):IO[Json]=for
    _<-ServiceClient.post("authorization","ensureaccess",Json.obj("userId"->user.id.asJson),true)
    profile<-identity(user)
    session<-ServiceClient.post("sessions","createsession",Json.obj("userId"->user.id.asJson,"credentialsVersion"->user.credentialsVersion.asJson),true)
  yield Json.obj("user"->profile,"sessionToken"->session.hcursor.get[String]("sessionToken").getOrElse(throw new IllegalStateException("Missing session token")).asJson,"expiresAt"->session.hcursor.get[String]("expiresAt").getOrElse("").asJson)
