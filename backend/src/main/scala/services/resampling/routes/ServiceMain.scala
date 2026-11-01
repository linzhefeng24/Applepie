package services.resampling.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("resampling",ResamplingRoutes.apiMessages,IO.unit)
