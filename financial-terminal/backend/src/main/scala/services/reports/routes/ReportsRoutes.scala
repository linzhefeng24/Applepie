package services.reports.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.reports.api.*
object ReportsRoutes:
  val apiMessages=List(
    register[ListReportsMessage,services.reports.objects.apiTypes.ListReportsResponse](classOf[ListReportsMessage].getSimpleName,permission="reports:read",ownerBound=true),
    register[SaveReportMessage,services.reports.objects.apiTypes.SaveReportResponse](classOf[SaveReportMessage].getSimpleName,permission="reports:write",ownerBound=true),
    register[DeleteReportMessage,services.reports.objects.apiTypes.DeleteReportResponse](classOf[DeleteReportMessage].getSimpleName,permission="reports:write",ownerBound=true)
  )
