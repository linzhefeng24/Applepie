package services.authorization.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("authorization",AuthorizationRoutes.apiMessages,Database.transaction(services.authorization.tables.AccessTable.AccessTableInitializer.initialize))
