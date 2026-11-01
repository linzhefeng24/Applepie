package services.performance.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.performance.api.*
object PerformanceRoutes:
  val apiMessages=List(
    register[GetPerformanceMessage,Json](classOf[GetPerformanceMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
