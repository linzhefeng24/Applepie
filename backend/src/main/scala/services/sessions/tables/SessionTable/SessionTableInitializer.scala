package services.sessions.tables.SessionTable
import cats.effect.IO
import java.sql.Connection
object SessionTableInitializer:
  private val createSql="CREATE SCHEMA IF NOT EXISTS sessions; CREATE TABLE IF NOT EXISTS sessions.session(id UUID PRIMARY KEY,user_id UUID NOT NULL,token_hash TEXT NOT NULL UNIQUE,credentials_version INT NOT NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),expires_at TIMESTAMPTZ NOT NULL,revoked_at TIMESTAMPTZ); CREATE INDEX IF NOT EXISTS session_owner ON sessions.session(user_id)"
  def initialize(c:Connection):IO[Unit]=IO.blocking{val s=c.createStatement();try s.execute(createSql) finally s.close();()}
