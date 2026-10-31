package services.watchlist.tables.WatchlistTable
import cats.effect.IO
import java.sql.Connection
object WatchlistTable:
  private val listSql = "SELECT symbol FROM portfolio.watchlist ORDER BY created_at,symbol"
  def list(connection: Connection): IO[List[String]] = IO.blocking {
    val s = connection.prepareStatement(listSql)
    try
      val r = s.executeQuery()
      try Iterator.continually(r.next()).takeWhile(identity).map(_ => r.getString(1)).toList
      finally r.close()
    finally s.close()
  }
  private val addSql = "INSERT INTO portfolio.watchlist(symbol) VALUES (?) ON CONFLICT DO NOTHING"
  def add(connection: Connection, symbol: String): IO[Unit] = IO.blocking {
    val s = connection.prepareStatement(addSql);
    try { s.setString(1, symbol); s.executeUpdate(); () }
    finally s.close()
  }
  private val removeSql = "DELETE FROM portfolio.watchlist WHERE symbol=?"
  def remove(connection: Connection, symbol: String): IO[Unit] = IO.blocking {
    val s = connection.prepareStatement(removeSql);
    try { s.setString(1, symbol); s.executeUpdate(); () }
    finally s.close()
  }
