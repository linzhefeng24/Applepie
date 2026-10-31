package services.watchlist.tables.WatchlistTable
import cats.effect.IO
import java.sql.Connection
object WatchlistTableInitializer:
  private val createSql =
    "CREATE SCHEMA IF NOT EXISTS portfolio; CREATE TABLE IF NOT EXISTS portfolio.watchlist(symbol TEXT PRIMARY KEY,created_at TIMESTAMPTZ NOT NULL DEFAULT now())"
  def initialize(connection: Connection): IO[Unit] = IO.blocking {
    val s = connection.createStatement();
    try { s.execute(createSql); () }
    finally s.close()
  }
