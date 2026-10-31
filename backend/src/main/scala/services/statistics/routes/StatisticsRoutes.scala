package services.statistics.routes
import io.circe.Json
import services.system.api.APIMessageRouter.register
import services.statistics.api.*
import services.statistics.objects.apiTypes.*
object StatisticsRoutes:
  val apiMessages = List(
    register[GetStockMessage, GetStockResponse](classOf[GetStockMessage].getSimpleName)
  )
