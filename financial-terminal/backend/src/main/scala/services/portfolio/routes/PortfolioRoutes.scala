package services.portfolio.routes
import io.circe.Json
import services.system.api.APIMessageRouter.register
import services.portfolio.api.*
import services.portfolio.objects.apiTypes.*
object PortfolioRoutes:
  val apiMessages = List(
    register[ListWatchlistMessage, WatchlistResponse](classOf[ListWatchlistMessage].getSimpleName),
    register[SetWatchlistMessage, WatchlistResponse](classOf[SetWatchlistMessage].getSimpleName),
    register[ListReportsMessage, ListReportsResponse](classOf[ListReportsMessage].getSimpleName),
    register[SaveReportMessage, SaveReportResponse](classOf[SaveReportMessage].getSimpleName),
    register[DeleteReportMessage, DeleteReportResponse](classOf[DeleteReportMessage].getSimpleName)
  )
