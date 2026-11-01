package services.accounts.tables.UserTable
import cats.effect.IO
import java.sql.Connection
object UserTableInitializer:
  private val createSql="CREATE SCHEMA IF NOT EXISTS accounts; CREATE TABLE IF NOT EXISTS accounts.users(id UUID PRIMARY KEY,username TEXT NOT NULL UNIQUE,display_name TEXT NOT NULL,password_hash TEXT NOT NULL,credentials_version INT NOT NULL DEFAULT 1,bootstrap BOOLEAN NOT NULL DEFAULT false,created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()); CREATE UNIQUE INDEX IF NOT EXISTS one_bootstrap_user ON accounts.users(bootstrap) WHERE bootstrap"
  def initialize(c:Connection):IO[Unit]=IO.blocking{val s=c.createStatement();try s.execute(createSql) finally s.close();()}
