package services.minute.tables.MinuteBarTable
import cats.effect.IO
import java.sql.Connection
import services.daily.objects.DailyBar
object MinuteBarTable:
  private val boundsSql="SELECT min(time)::text,max(time)::text,count(*) FROM history.minute_bar WHERE symbol=?"
  def bounds(c:Connection,symbol:String):IO[Option[(String,String,Long)]]=IO.blocking {
    val s=c.prepareStatement(boundsSql)
    try
      s.setString(1,symbol);val r=s.executeQuery()
      try if r.next() && r.getLong(3)>0 then Some((r.getString(1),r.getString(2),r.getLong(3))) else None finally r.close()
    finally s.close()
  }

  private val rawSql="SELECT to_char(time,'YYYY-MM-DD HH24:MI:SS'),open,high,low,close,volume FROM history.minute_bar WHERE symbol=? AND time>=?::date AND time<(?::date+INTERVAL '1 day') ORDER BY time LIMIT 50001"
  def raw(c:Connection,symbol:String,start:String,end:String):IO[List[DailyBar]]=IO.blocking {
    val s=c.prepareStatement(rawSql)
    try {s.setString(1,symbol);s.setString(2,start);s.setString(3,end);val r=s.executeQuery();try Iterator.continually(r.next()).takeWhile(identity).map(_=>DailyBar(r.getString(1),r.getDouble(2),r.getDouble(3),r.getDouble(4),r.getDouble(5),r.getLong(6),1)).toList finally r.close()} finally s.close()
  }
