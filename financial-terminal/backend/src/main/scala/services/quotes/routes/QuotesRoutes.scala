package services.quotes.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.quotes.api.*
object QuotesRoutes:
  val apiMessages=List(
    register[ListQuotesMessage,Json](classOf[ListQuotesMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
