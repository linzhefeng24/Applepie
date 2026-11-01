package services.minute.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("minute",MinuteRoutes.apiMessages,Database.transaction(c=>services.minute.tables.MinuteBarTable.MinuteBarTableInitializer.initialize(c,java.nio.file.Path.of(sys.env("DATA_DIR")))))
