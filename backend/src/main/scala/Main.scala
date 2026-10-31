import cats.effect.{IO, IOApp}
import com.comcast.ip4s.{Host, Port}
import java.nio.file.Path
import org.http4s.ember.server.EmberServerBuilder
import org.http4s.server.middleware.{CORS, ErrorAction}
import services.system.Database
import services.system.api.APIMessageRouter
import services.market.routes.MarketRoutes
import services.portfolio.routes.PortfolioRoutes
import services.analysis.routes.AnalysisRoutes
import services.market.tables.StockTable.StockTableInitializer
import services.market.tables.DailyBarTable.DailyBarTableInitializer
import services.portfolio.tables.WatchlistTable.WatchlistTableInitializer
import services.portfolio.tables.ReportTable.ReportTableInitializer
object Main extends IOApp.Simple:
  private val service = sys.env.getOrElse("SERVICE", "market")
  private val portNumber = sys.env
    .getOrElse(
      "HTTP_PORT",
      Map("market" -> "8101", "portfolio" -> "8102", "analysis" -> "8103")(service)
    )
    .toInt
  private val data = Path.of(sys.env.getOrElse("DATA_DIR", "data"))
  private val initialize: IO[Unit] = service match
    case "market" =>
      Database.transaction(c =>
        StockTableInitializer.initialize(c, data) *> DailyBarTableInitializer.initialize(c, data)
      )
    case "portfolio" =>
      Database.transaction(c =>
        WatchlistTableInitializer.initialize(c) *> ReportTableInitializer.initialize(c)
      )
    case "analysis" => IO.unit
    case _          => IO.raiseError(new IllegalArgumentException("Unknown SERVICE"))
  private val entries = service match
    case "market"    => MarketRoutes.apiMessages
    case "portfolio" => PortfolioRoutes.apiMessages
    case "analysis"  => AnalysisRoutes.apiMessages
    case _           => Nil
  def run: IO[Unit] = initialize *> EmberServerBuilder
    .default[IO]
    .withHost(Host.fromString(sys.env.getOrElse("SERVICE_HOST", "127.0.0.1")).get)
    .withPort(Port.fromInt(portNumber).get)
    .withHttpApp(APIMessageRouter.routes(service, entries).orNotFound)
    .build
    .use(_ => IO.println(s"$service ready on $portNumber") *> IO.never)
