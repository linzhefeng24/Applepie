package services.catalog.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("catalog",CatalogRoutes.apiMessages,Database.transaction(c=>services.catalog.tables.StockTable.StockTableInitializer.initialize(c,java.nio.file.Path.of(sys.env("DATA_DIR")))))
