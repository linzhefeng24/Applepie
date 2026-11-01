package services.statistics.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.statistics.api.*
object StatisticsRoutes:
  val apiMessages=List(
    register[GetStockMessage,services.statistics.objects.apiTypes.GetStockResponse](classOf[GetStockMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
