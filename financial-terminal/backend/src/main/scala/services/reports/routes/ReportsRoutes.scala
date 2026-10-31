package services.reports.routes
import io.circe.Json
import services.system.api.APIMessageRouter.register
import services.reports.api.*
import services.reports.objects.apiTypes.*
object ReportsRoutes:
  val apiMessages = List(
    register[ListReportsMessage, ListReportsResponse](classOf[ListReportsMessage].getSimpleName),
    register[SaveReportMessage, SaveReportResponse](classOf[SaveReportMessage].getSimpleName),
    register[DeleteReportMessage, DeleteReportResponse](classOf[DeleteReportMessage].getSimpleName)
  )
