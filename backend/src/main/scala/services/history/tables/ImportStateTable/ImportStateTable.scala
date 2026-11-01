package services.history.tables.ImportStateTable
import cats.effect.IO
import java.sql.Connection
object ImportStateTable:
  def matches(c: Connection, sha: String): IO[Boolean] = IO.blocking {
    val s=c.prepareStatement("SELECT sha256 FROM history.import_state WHERE name='minutes'")
    try
      val r=s.executeQuery()
      try r.next() && r.getString(1)==sha finally r.close()
    finally s.close()
  }
  def mark(c: Connection, sha: String): IO[Unit] = IO.blocking {
    val s=c.prepareStatement("INSERT INTO history.import_state(name,sha256) VALUES ('minutes',?) ON CONFLICT(name) DO UPDATE SET sha256=EXCLUDED.sha256")
    try
      s.setString(1,sha); s.executeUpdate(); ()
    finally s.close()
  }
