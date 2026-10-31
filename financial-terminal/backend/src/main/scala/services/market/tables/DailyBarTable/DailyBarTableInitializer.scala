package services.market.tables.DailyBarTable
import cats.effect.IO
import java.sql.Connection
import java.nio.file.{Files, Path}
import org.postgresql.PGConnection
object DailyBarTableInitializer:
  private val createSql =
    "CREATE TABLE IF NOT EXISTS market.daily_bar(symbol TEXT REFERENCES market.stock(symbol),date DATE,open DOUBLE PRECISION NOT NULL,high DOUBLE PRECISION NOT NULL,low DOUBLE PRECISION NOT NULL,close DOUBLE PRECISION NOT NULL CHECK(close>0),volume BIGINT NOT NULL CHECK(volume>=0),minutes INT NOT NULL,PRIMARY KEY(symbol,date))"
  def initialize(connection: Connection, data: Path): IO[Unit] = IO.blocking {
    val s = connection.createStatement()
    try
      s.execute(createSql)
      // Transactional refresh makes startup reproducible without touching research records.
      s.execute("DELETE FROM market.daily_bar")
      val reader = Files.newBufferedReader(data.resolve("daily.csv"))
      try
        connection
          .unwrap(classOf[PGConnection])
          .getCopyAPI
          .copyIn(
            "COPY market.daily_bar(symbol,date,open,high,low,close,volume,minutes) FROM STDIN CSV HEADER",
            reader
          )
      finally reader.close()
      ()
    finally s.close()
  }
