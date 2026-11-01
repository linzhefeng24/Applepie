package services.history.tables.MinuteBarTable
import cats.effect.IO
import java.sql.Connection
import java.nio.file.{Files,Path}
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.util.zip.GZIPInputStream
import org.postgresql.PGConnection
import io.circe.parser.parse
import services.history.tables.ImportStateTable.{ImportStateTable,ImportStateTableInitializer}
object MinuteBarTableInitializer:
  private def sha(bytes: Array[Byte]): String=MessageDigest.getInstance("SHA-256").digest(bytes).map(b=>f"${b & 0xff}%02x").mkString
  def initialize(c: Connection,data: Path): IO[Unit] =
    val root=data.resolve("minutes");val manifest=root.resolve("manifest.json")
    for
      _ <- ImportStateTableInitializer.initialize(c)
      _ <- IO.blocking {
        val s=c.createStatement()
        try s.execute("CREATE TABLE IF NOT EXISTS history.minute_bar(symbol TEXT REFERENCES market.stock(symbol),time TIMESTAMP WITHOUT TIME ZONE,open DOUBLE PRECISION NOT NULL,high DOUBLE PRECISION NOT NULL,low DOUBLE PRECISION NOT NULL,close DOUBLE PRECISION NOT NULL CHECK(close>0),volume BIGINT NOT NULL CHECK(volume>=0),PRIMARY KEY(symbol,time))")
        finally s.close()
      }
      exists <- IO.blocking(Files.exists(manifest))
      _ <- if !exists then IO.unit else
        for
          bytes <- IO.blocking(Files.readAllBytes(manifest))
          digest=sha(bytes)
          current <- ImportStateTable.matches(c,digest)
          _ <- if current then IO.unit else
            IO.blocking {
              val entries=parse(new String(bytes,StandardCharsets.UTF_8)).fold(throw _,identity).hcursor.get[List[io.circe.Json]]("symbols").fold(throw _,identity)
              val s=c.createStatement()
              try s.execute("DELETE FROM history.minute_bar") finally s.close()
              entries.foreach { entry =>
                val cursor=entry.hcursor
                val symbol=cursor.get[String]("symbol").fold(throw _,identity)
                val filename=cursor.get[String]("file").fold(throw _,identity)
                require(symbol.matches("[A-Z][A-Z0-9-]{0,14}") && filename==s"$symbol.csv.gz","Invalid minute source filename")
                val file=root.resolve(filename)
                require(sha(Files.readAllBytes(file))==cursor.get[String]("sha256").fold(throw _,identity),s"Minute source checksum failed: $symbol")
                val reader=new InputStreamReader(new GZIPInputStream(Files.newInputStream(file)),StandardCharsets.UTF_8)
                try c.unwrap(classOf[PGConnection]).getCopyAPI.copyIn("COPY history.minute_bar(symbol,time,open,high,low,close,volume) FROM STDIN CSV HEADER",reader)
                finally reader.close()
              }
            } *> ImportStateTable.mark(c,digest)
        yield ()
    yield ()
