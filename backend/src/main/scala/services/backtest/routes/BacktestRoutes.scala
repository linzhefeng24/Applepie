package services.backtest.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.backtest.api.*
object BacktestRoutes:
  val apiMessages=List(
    register[RunBacktestMessage,Json](classOf[RunBacktestMessage].getSimpleName,permission="research:compute",ownerBound=false)
  )
