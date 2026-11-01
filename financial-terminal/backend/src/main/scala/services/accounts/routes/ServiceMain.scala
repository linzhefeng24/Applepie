package services.accounts.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("accounts",AccountsRoutes.apiMessages,Database.transaction(services.accounts.tables.UserTable.UserTableInitializer.initialize))
