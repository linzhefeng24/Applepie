package services.catalog.tables.StockTable
import cats.effect.IO
import java.sql.Connection
import java.nio.file.{Files, Path}
import io.circe.parser.decode
import services.catalog.objects.Stock
object StockTableInitializer:
  private val createSql =
    "CREATE SCHEMA IF NOT EXISTS market; CREATE TABLE IF NOT EXISTS market.stock(symbol TEXT PRIMARY KEY,name TEXT NOT NULL,sector TEXT NOT NULL,currency TEXT NOT NULL,first_date DATE NOT NULL,last_date DATE NOT NULL,sessions INT NOT NULL,source TEXT NOT NULL)"
  def initialize(connection: Connection, data: Path): IO[Unit] = IO.blocking {
    val s = connection.createStatement();
    try s.execute(createSql)
    finally s.close()
    val stocks =
      decode[List[Stock]](Files.readString(data.resolve("stocks.json"))).fold(throw _, identity)
    val insert = connection.prepareStatement(
      "INSERT INTO market.stock VALUES (?,?,?,?,?::date,?::date,?,?) ON CONFLICT(symbol) DO UPDATE SET name=EXCLUDED.name,sector=EXCLUDED.sector,first_date=EXCLUDED.first_date,last_date=EXCLUDED.last_date,sessions=EXCLUDED.sessions,source=EXCLUDED.source"
    )
    try
      stocks.foreach { stock =>
        insert.setString(1, stock.symbol); insert.setString(2, stock.name);
        insert.setString(3, stock.sector); insert.setString(4, stock.currency);
        insert.setString(5, stock.firstDate); insert.setString(6, stock.lastDate);
        insert.setInt(7, stock.sessions); insert.setString(8, stock.source); insert.addBatch()
      }
      insert.executeBatch(); ()
    finally insert.close()
  }
