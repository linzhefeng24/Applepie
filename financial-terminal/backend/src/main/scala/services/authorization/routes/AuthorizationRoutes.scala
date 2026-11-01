package services.authorization.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.authorization.api.*
object AuthorizationRoutes:
  val apiMessages=List(
    register[ListUsersMessage,Json](classOf[ListUsersMessage].getSimpleName,permission="users:manage",ownerBound=false),
    register[SetAccessMessage,Json](classOf[SetAccessMessage].getSimpleName,permission="users:manage",ownerBound=false),
    registerInternal[EnsureAccessMessage,Json](classOf[EnsureAccessMessage].getSimpleName,Set("accounts")),
    registerInternal[ResolveIdentityMessage,Json](classOf[ResolveIdentityMessage].getSimpleName,Set())
  )
