package services.history.tables.MinuteBarTable
import cats.effect.IO
import java.sql.Connection
import services.history.objects.DailyBar
object MinuteBarTable:
  private val boundsSql="SELECT min(time)::text,max(time)::text,count(*) FROM history.minute_bar WHERE symbol=?"
  def bounds(c:Connection,symbol:String):IO[Option[(String,String,Long)]]=IO.blocking {
    val s=c.prepareStatement(boundsSql)
    try
      s.setString(1,symbol);val r=s.executeQuery()
      try if r.next() && r.getLong(3)>0 then Some((r.getString(1),r.getString(2),r.getLong(3))) else None finally r.close()
    finally s.close()
  }
  private val barsSql="""SELECT to_char(bucket,'YYYY-MM-DD HH24:MI:SS'),(array_agg(open ORDER BY time))[1],max(high),min(low),(array_agg(close ORDER BY time DESC))[1],sum(volume),count(*) FROM (SELECT *,date_bin(?::interval,time,TIMESTAMP '2000-01-01') AS bucket FROM history.minute_bar WHERE symbol=? AND time>=?::date AND time<(?::date+INTERVAL '1 day')) q GROUP BY bucket ORDER BY bucket LIMIT 5001"""
  def aggregate(c:Connection,symbol:String,start:String,end:String,frequency:String):IO[List[DailyBar]]=IO.blocking {
    val interval=Map("1min"->"1 minute","2min"->"2 minutes","5min"->"5 minutes").getOrElse(frequency,throw new IllegalArgumentException("Unsupported minute frequency"))
    val s=c.prepareStatement(barsSql)
    try
      s.setString(1,interval);s.setString(2,symbol);s.setString(3,start);s.setString(4,end)
      val r=s.executeQuery()
      try Iterator.continually(r.next()).takeWhile(identity).map(_=>DailyBar(r.getString(1),r.getDouble(2),r.getDouble(3),r.getDouble(4),r.getDouble(5),r.getLong(6),r.getInt(7))).toList finally r.close()
    finally s.close()
  }
