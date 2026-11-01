package services.reports.tables.ReportTable
import cats.effect.IO
import java.sql.Connection
object ReportTableInitializer:
  private val createSql="CREATE SCHEMA IF NOT EXISTS reports; CREATE TABLE IF NOT EXISTS reports.report(id UUID PRIMARY KEY,user_id UUID NOT NULL,title TEXT NOT NULL,kind TEXT NOT NULL CHECK(kind IN ('analysis','backtest')),created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),parameters JSONB NOT NULL,result JSONB NOT NULL); CREATE INDEX IF NOT EXISTS report_owner ON reports.report(user_id,created_at DESC)"
  def initialize(c:Connection):IO[Unit]=IO.blocking{val s=c.createStatement();try s.execute(createSql) finally s.close();()}
