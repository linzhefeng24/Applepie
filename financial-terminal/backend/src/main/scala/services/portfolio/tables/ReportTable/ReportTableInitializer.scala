package services.portfolio.tables.ReportTable
import cats.effect.IO
import java.sql.Connection
object ReportTableInitializer:
  private val createSql =
    "CREATE TABLE IF NOT EXISTS portfolio.report(id UUID PRIMARY KEY,title TEXT NOT NULL,kind TEXT NOT NULL,parameters JSONB NOT NULL,result JSONB NOT NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT now())"
  def initialize(connection: Connection): IO[Unit] = IO.blocking {
    val s = connection.createStatement();
    try { s.execute(createSql); () }
    finally s.close()
  }
