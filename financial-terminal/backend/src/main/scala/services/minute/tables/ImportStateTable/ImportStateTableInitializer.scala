package services.minute.tables.ImportStateTable
import cats.effect.IO
import java.sql.Connection
object ImportStateTableInitializer:
  private val createSql="CREATE SCHEMA IF NOT EXISTS history; CREATE TABLE IF NOT EXISTS history.import_state(name TEXT PRIMARY KEY,sha256 TEXT NOT NULL)"
  def initialize(c:Connection):IO[Unit]=IO.blocking {
    val s=c.createStatement()
    try s.execute(createSql) finally s.close()
    ()
  }
