package services.daily.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("daily",DailyRoutes.apiMessages,Database.transaction(c=>services.daily.tables.DailyBarTable.DailyBarTableInitializer.initialize(c,java.nio.file.Path.of(sys.env("DATA_DIR")))))
