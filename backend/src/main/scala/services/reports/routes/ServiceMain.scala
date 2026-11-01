package services.reports.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("reports",ReportsRoutes.apiMessages,Database.transaction(services.reports.tables.ReportTable.ReportTableInitializer.initialize))
