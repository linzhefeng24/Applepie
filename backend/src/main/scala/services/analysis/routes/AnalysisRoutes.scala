package services.analysis.routes
import io.circe.Json
import services.system.api.APIMessageRouter.register
import services.analysis.api.*
object AnalysisRoutes:
  val apiMessages = List(
    register[RunAnalysisMessage, Json](classOf[RunAnalysisMessage].getSimpleName),
    register[RunBacktestMessage, Json](classOf[RunBacktestMessage].getSimpleName)
  )
