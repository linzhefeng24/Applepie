package services.authorization.tables.AccessTable
import cats.effect.IO
import java.sql.Connection
object AccessTableInitializer:
  private val createSql="CREATE SCHEMA IF NOT EXISTS access_control; CREATE TABLE IF NOT EXISTS access_control.access(user_id UUID PRIMARY KEY,role TEXT NOT NULL CHECK(role IN ('admin','analyst','viewer')),enabled BOOLEAN NOT NULL DEFAULT true)"
  def initialize(c:Connection):IO[Unit]=IO.blocking{val s=c.createStatement();try s.execute(createSql) finally s.close();()}
