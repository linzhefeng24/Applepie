package services.catalog.tables.StockTable
import cats.effect.IO
import java.sql.Connection
import services.catalog.objects.Stock
object StockTable:
  private val listSql =
    "SELECT symbol,name,sector,currency,first_date::text,last_date::text,sessions,source FROM market.stock ORDER BY symbol"
  def list(connection: Connection): IO[List[Stock]] = IO.blocking {
    val s = connection.prepareStatement(listSql)
    try
      val r = s.executeQuery()
      try
        Iterator
          .continually(r.next())
          .takeWhile(identity)
          .map(_ =>
            Stock(
              r.getString(1),
              r.getString(2),
              r.getString(3),
              r.getString(4),
              r.getString(5),
              r.getString(6),
              r.getInt(7),
              r.getString(8)
            )
          )
          .toList
      finally r.close()
    finally s.close()
  }
