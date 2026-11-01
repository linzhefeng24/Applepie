package services.watchlist.tables.WatchlistTable
import cats.effect.IO
import java.sql.Connection
object WatchlistTable:
  private val listSql = "SELECT symbol FROM watchlist.watchlist WHERE user_id=?::uuid ORDER BY created_at,symbol"
  def list(connection: Connection,userId:String): IO[List[String]] = IO.blocking {
    val s = connection.prepareStatement(listSql)
    try
      s.setString(1,userId); val r = s.executeQuery()
      try Iterator.continually(r.next()).takeWhile(identity).map(_ => r.getString(1)).toList
      finally r.close()
    finally s.close()
  }
  private val addSql = "INSERT INTO watchlist.watchlist(user_id,symbol) VALUES (?::uuid,?) ON CONFLICT DO NOTHING"
  def add(connection: Connection,userId:String, symbol: String): IO[Unit] = IO.blocking {
    val s = connection.prepareStatement(addSql);
    try { s.setString(1,userId);s.setString(2, symbol); s.executeUpdate(); () }
    finally s.close()
  }
  private val removeSql = "DELETE FROM watchlist.watchlist WHERE user_id=?::uuid AND symbol=?"
  def remove(connection: Connection,userId:String, symbol: String): IO[Unit] = IO.blocking {
    val s = connection.prepareStatement(removeSql);
    try { s.setString(1,userId);s.setString(2, symbol); s.executeUpdate(); () }
    finally s.close()
  }
