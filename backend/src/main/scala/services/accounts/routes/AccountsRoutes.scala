package services.accounts.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.accounts.api.*
object AccountsRoutes:
  val apiMessages=List(
    register[RegisterUserMessage,Json](classOf[RegisterUserMessage].getSimpleName,permission="public",ownerBound=false,issueCookie=true),
    register[LoginUserMessage,Json](classOf[LoginUserMessage].getSimpleName,permission="public",ownerBound=false,issueCookie=true),
    register[GetBootstrapInfoMessage,Json](classOf[GetBootstrapInfoMessage].getSimpleName,permission="public",ownerBound=false),
    register[GetCurrentUserMessage,Json](classOf[GetCurrentUserMessage].getSimpleName,permission="profile:self",ownerBound=true),
    register[UpdateProfileMessage,Json](classOf[UpdateProfileMessage].getSimpleName,permission="profile:self",ownerBound=true),
    register[ChangePasswordMessage,Json](classOf[ChangePasswordMessage].getSimpleName,permission="profile:self",ownerBound=true,clearCookie=true),
    registerInternal[FindUserMessage,Json](classOf[FindUserMessage].getSimpleName,Set("accounts","authorization","sessions")),
    registerInternal[FindUsersMessage,Json](classOf[FindUsersMessage].getSimpleName,Set("authorization"))
  )
