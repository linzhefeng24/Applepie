package services.watchlist.tables.WatchlistTable
import cats.effect.IO
import java.sql.Connection
object WatchlistTableInitializer:
  private val createSql="CREATE SCHEMA IF NOT EXISTS watchlist; CREATE TABLE IF NOT EXISTS watchlist.watchlist(user_id UUID NOT NULL,symbol TEXT NOT NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),PRIMARY KEY(user_id,symbol))"
  def initialize(c:Connection):IO[Unit]=IO.blocking{val s=c.createStatement();try s.execute(createSql) finally s.close();()}
