package services.daily.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.daily.api.*
object DailyRoutes:
  val apiMessages=List(
    register[GetPricesMessage,services.daily.objects.apiTypes.GetPricesResponse](classOf[GetPricesMessage].getSimpleName,permission="data:read",ownerBound=false),
    register[GetCoverageMessage,Json](classOf[GetCoverageMessage].getSimpleName,permission="data:read",ownerBound=false),
    register[GetTailBarsMessage,services.daily.objects.apiTypes.GetPricesResponse](classOf[GetTailBarsMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
