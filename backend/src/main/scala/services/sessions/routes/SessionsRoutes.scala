package services.sessions.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.sessions.api.*
object SessionsRoutes:
  val apiMessages=List(
    register[GetSessionsMessage,Json](classOf[GetSessionsMessage].getSimpleName,permission="sessions:self",ownerBound=true,withSession=true),
    register[LogoutUserMessage,Json](classOf[LogoutUserMessage].getSimpleName,permission="sessions:self",ownerBound=true,withSession=true,clearCookie=true),
    register[LogoutAllMessage,Json](classOf[LogoutAllMessage].getSimpleName,permission="sessions:self",ownerBound=true,clearCookie=true),
    register[RevokeSessionMessage,Json](classOf[RevokeSessionMessage].getSimpleName,permission="sessions:self",ownerBound=true),
    registerInternal[CreateSessionMessage,Json](classOf[CreateSessionMessage].getSimpleName,Set("accounts")),
    registerInternal[ValidateSessionMessage,Json](classOf[ValidateSessionMessage].getSimpleName,Set()),
    registerInternal[RevokeAllInternalMessage,Json](classOf[RevokeAllInternalMessage].getSimpleName,Set("accounts"))
  )
