package services.optimization.routes
import io.circe.Json
import services.system.api.APIMessageRouter.register
import services.optimization.api.*
object OptimizationRoutes:
  val apiMessages = List(
    register[RunAnalysisMessage, Json](classOf[RunAnalysisMessage].getSimpleName)
  )
