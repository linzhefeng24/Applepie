package services.watchlist.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.watchlist.api.*
object WatchlistRoutes:
  val apiMessages=List(
    register[ListWatchlistMessage,services.watchlist.objects.apiTypes.WatchlistResponse](classOf[ListWatchlistMessage].getSimpleName,permission="watchlist:read",ownerBound=true),
    register[SetWatchlistMessage,services.watchlist.objects.apiTypes.WatchlistResponse](classOf[SetWatchlistMessage].getSimpleName,permission="watchlist:write",ownerBound=true)
  )
