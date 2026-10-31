package services.market.tables.DailyBarTable
import cats.effect.IO
import java.sql.Connection
import services.market.objects.DailyBar
object DailyBarTable:
  private val findSql =
    "SELECT date::text,open,high,low,close,volume,minutes FROM market.daily_bar WHERE symbol=? AND date BETWEEN ?::date AND ?::date ORDER BY date"
  def find(connection: Connection, symbol: String, start: String, end: String): IO[List[DailyBar]] =
    IO.blocking {
      val s = connection.prepareStatement(findSql)
      try
        s.setString(1, symbol); s.setString(2, start); s.setString(3, end)
        val r = s.executeQuery()
        try
          Iterator
            .continually(r.next())
            .takeWhile(identity)
            .map(_ =>
              DailyBar(
                r.getString(1),
                r.getDouble(2),
                r.getDouble(3),
                r.getDouble(4),
                r.getDouble(5),
                r.getLong(6),
                r.getInt(7)
              )
            )
            .toList
        finally r.close()
      finally s.close()
    }

  private val latestSql =
    "SELECT DISTINCT ON (symbol) symbol,date::text,close,volume,prior_close FROM (SELECT symbol,date,close,volume,lag(close) OVER (PARTITION BY symbol ORDER BY date) AS prior_close FROM market.daily_bar) q ORDER BY symbol,date DESC"
  def latest(connection: Connection): IO[io.circe.Json] = IO.blocking {
    import io.circe.Json
    import io.circe.syntax.*
    val s = connection.prepareStatement(latestSql)
    try
      val r = s.executeQuery()
      try
        Json.obj(
          Iterator
            .continually(r.next())
            .takeWhile(identity)
            .map(_ =>
              r.getString(1) -> Json.obj(
                "date" -> r.getString(2).asJson,
                "close" -> r.getDouble(3).asJson,
                "volume" -> r.getLong(4).asJson,
                "changePct" -> (r.getDouble(3) / r.getDouble(5) - 1).asJson
              )
            )
            .toSeq*
        )
      finally r.close()
    finally s.close()
  }
