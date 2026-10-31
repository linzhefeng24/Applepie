package services.history.routes
import io.circe.Json
import services.system.api.APIMessageRouter.register
import services.history.api.*
import services.history.objects.apiTypes.*
object HistoryRoutes:
  val apiMessages = List(
    register[GetPricesMessage, GetPricesResponse](classOf[GetPricesMessage].getSimpleName)
  )
