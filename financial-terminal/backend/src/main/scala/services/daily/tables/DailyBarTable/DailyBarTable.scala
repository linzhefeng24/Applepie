package services.daily.tables.DailyBarTable
import cats.effect.IO
import java.sql.Connection
import services.daily.objects.DailyBar
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


  def symbols(connection:Connection):IO[List[String]]=IO.blocking {
    val s=connection.createStatement();try {val r=s.executeQuery("SELECT DISTINCT symbol FROM market.daily_bar ORDER BY symbol");try Iterator.continually(r.next()).takeWhile(identity).map(_=>r.getString(1)).toList finally r.close()} finally s.close()
  }
  def bounds(connection:Connection,symbol:String):IO[Option[(String,String,Long)]]=IO.blocking {
    val s=connection.prepareStatement("SELECT min(date)::text,max(date)::text,count(*) FROM market.daily_bar WHERE symbol=?")
    try {s.setString(1,symbol);val r=s.executeQuery();try if r.next()&&r.getLong(3)>0 then Some((r.getString(1),r.getString(2),r.getLong(3))) else None finally r.close()} finally s.close()
  }
  def tails(connection:Connection):IO[Map[String,List[DailyBar]]]=IO.blocking {
    val s=connection.createStatement()
    try {val r=s.executeQuery("SELECT symbol,date::text,open,high,low,close,volume,minutes FROM (SELECT *,row_number() OVER (PARTITION BY symbol ORDER BY date DESC) AS rank FROM market.daily_bar) q WHERE rank<=2 ORDER BY symbol,date")
      try Iterator.continually(r.next()).takeWhile(identity).map(_=>(r.getString(1),DailyBar(r.getString(2),r.getDouble(3),r.getDouble(4),r.getDouble(5),r.getDouble(6),r.getLong(7),r.getInt(8)))).toList.groupMap(_._1)(_._2) finally r.close()
    } finally s.close()
  }
