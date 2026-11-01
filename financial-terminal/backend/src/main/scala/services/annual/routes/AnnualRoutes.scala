package services.annual.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.annual.api.*
object AnnualRoutes:
  val apiMessages=List(
    register[GetAnnualMessage,Json](classOf[GetAnnualMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
