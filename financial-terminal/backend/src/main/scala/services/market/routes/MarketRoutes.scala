package services.market.routes
import io.circe.Json
import services.system.api.APIMessageRouter.register
import services.market.api.*
import services.market.objects.apiTypes.*
object MarketRoutes:
  val apiMessages = List(
    register[ListStocksMessage, ListStocksResponse](classOf[ListStocksMessage].getSimpleName),
    register[GetStockMessage, GetStockResponse](classOf[GetStockMessage].getSimpleName),
    register[GetPricesMessage, GetPricesResponse](classOf[GetPricesMessage].getSimpleName)
  )
