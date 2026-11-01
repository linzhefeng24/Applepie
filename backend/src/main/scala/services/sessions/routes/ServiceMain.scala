package services.sessions.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("sessions",SessionsRoutes.apiMessages,Database.transaction(services.sessions.tables.SessionTable.SessionTableInitializer.initialize))
