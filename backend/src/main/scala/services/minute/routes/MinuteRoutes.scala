package services.minute.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.minute.api.*
object MinuteRoutes:
  val apiMessages=List(
    register[GetMinutePricesMessage,Json](classOf[GetMinutePricesMessage].getSimpleName,permission="data:read",ownerBound=false),
    register[GetCoverageMessage,Json](classOf[GetCoverageMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
