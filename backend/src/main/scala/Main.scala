import cats.effect.{IO, IOApp}
import com.comcast.ip4s.{Host, Port}
import java.nio.file.Path
import org.http4s.ember.server.EmberServerBuilder
import services.system.Database
import services.system.api.APIMessageRouter
import services.market.routes.MarketRoutes
import services.history.routes.HistoryRoutes
import services.statistics.routes.StatisticsRoutes
import services.watchlist.routes.WatchlistRoutes
import services.reports.routes.ReportsRoutes
import services.optimization.routes.OptimizationRoutes
import services.backtest.routes.BacktestRoutes
import services.market.tables.StockTable.StockTableInitializer
import services.history.tables.DailyBarTable.DailyBarTableInitializer
import services.watchlist.tables.WatchlistTable.WatchlistTableInitializer
import services.reports.tables.ReportTable.ReportTableInitializer

/** One executable per bounded service, sharing only platform bootstrap infrastructure. */
object Main extends IOApp.Simple:
  private val service = sys.env.getOrElse("SERVICE", "market")
  private val defaults = Map("market" -> 8101, "watchlist" -> 8102, "optimization" -> 8103,
    "backtest" -> 8105, "history" -> 8106, "statistics" -> 8107, "reports" -> 8108)
  private val portNumber = sys.env.get("HTTP_PORT").map(_.toInt).getOrElse(defaults(service))
  private val data = Path.of(sys.env.getOrElse("DATA_DIR", "data"))
  private val initialize: IO[Unit] = service match
    case "market" => Database.transaction(c => StockTableInitializer.initialize(c, data))
    case "history" => Database.transaction(c => DailyBarTableInitializer.initialize(c, data))
    case "watchlist" => Database.transaction(WatchlistTableInitializer.initialize)
    case "reports" => Database.transaction(ReportTableInitializer.initialize)
    case "statistics" | "optimization" | "backtest" => IO.unit
    case _ => IO.raiseError(new IllegalArgumentException("Unknown SERVICE"))
  private val entries = service match
    case "market" => MarketRoutes.apiMessages
    case "history" => HistoryRoutes.apiMessages
    case "statistics" => StatisticsRoutes.apiMessages
    case "watchlist" => WatchlistRoutes.apiMessages
    case "reports" => ReportsRoutes.apiMessages
    case "optimization" => OptimizationRoutes.apiMessages
    case "backtest" => BacktestRoutes.apiMessages
    case _ => Nil
  def run: IO[Unit] = initialize *> EmberServerBuilder
    .default[IO]
    .withHost(Host.fromString(sys.env.getOrElse("SERVICE_HOST", "127.0.0.1")).get)
    .withPort(Port.fromInt(portNumber).get)
    .withHttpApp(APIMessageRouter.routes(service, entries).orNotFound)
    .build.use(_ => IO.println(s"$service ready on $portNumber") *> IO.never)
