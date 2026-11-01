package services.risk.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.risk.api.*
object RiskRoutes:
  val apiMessages=List(
    register[GetRiskMessage,Json](classOf[GetRiskMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
