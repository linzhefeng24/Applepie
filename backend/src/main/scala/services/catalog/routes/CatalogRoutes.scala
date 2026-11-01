package services.catalog.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.catalog.api.*
object CatalogRoutes:
  val apiMessages=List(
    register[ListSecuritiesMessage,Json](classOf[ListSecuritiesMessage].getSimpleName,permission="data:read",ownerBound=false),
    register[GetSecurityMessage,services.catalog.objects.Stock](classOf[GetSecurityMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
