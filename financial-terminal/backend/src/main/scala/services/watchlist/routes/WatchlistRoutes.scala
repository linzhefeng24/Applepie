package services.watchlist.routes
import io.circe.Json
import services.system.api.APIMessageRouter.register
import services.watchlist.api.*
import services.watchlist.objects.apiTypes.*
object WatchlistRoutes:
  val apiMessages = List(
    register[ListWatchlistMessage, WatchlistResponse](classOf[ListWatchlistMessage].getSimpleName),
    register[SetWatchlistMessage, WatchlistResponse](classOf[SetWatchlistMessage].getSimpleName)
  )
