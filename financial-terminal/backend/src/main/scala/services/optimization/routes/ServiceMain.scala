package services.optimization.routes
import cats.effect.{IO,IOApp}
import services.system.{Database,ServiceServer}
object ServiceMain extends IOApp.Simple:
  def run:IO[Unit]=ServiceServer.run("optimization",OptimizationRoutes.apiMessages,IO.unit)
