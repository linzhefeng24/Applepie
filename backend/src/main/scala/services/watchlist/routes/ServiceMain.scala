package services.watchlist.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("watchlist",WatchlistRoutes.apiMessages,Database.transaction(services.watchlist.tables.WatchlistTable.WatchlistTableInitializer.initialize))
