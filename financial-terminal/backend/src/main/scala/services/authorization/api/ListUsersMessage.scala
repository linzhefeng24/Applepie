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
final case class ListUsersMessage() extends ComposedMessage[Json]:
  def plan: IO[Json] =
    for
      users<-ServiceClient.post("accounts","findusers",Json.obj(),true).flatMap(j=>IO.fromEither(j.as[List[Json]]))
      access<-Database.transaction(AccessTable.all)
    yield Json.obj("users"->users.map { user=>
      val id=user.hcursor.get[String]("id").getOrElse("");val state=access.getOrElse(id,("analyst",false))
      Json.obj("id"->id.asJson,"username"->user.hcursor.get[String]("username").getOrElse("").asJson,"displayName"->user.hcursor.get[String]("displayName").getOrElse("").asJson,"role"->state._1.asJson,"enabled"->state._2.asJson)
    }.asJson)
object ListUsersMessage:
  given Decoder[ListUsersMessage]=deriveDecoder
