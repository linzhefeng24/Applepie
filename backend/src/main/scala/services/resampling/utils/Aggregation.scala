package services.resampling.utils
import services.daily.objects.DailyBar
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
private[resampling] object Aggregation:
  private val timestamp=DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
  def aggregate(bars:List[DailyBar],frequency:String):List[DailyBar]=
    if frequency=="1d"||frequency=="1min" then bars else
      bars.groupBy { bar=> frequency match
        case "1mo"=>bar.date.take(7)+"-01"
        case "1y"=>bar.date.take(4)+"-01-01"
        case "2min"|"5min"=>
          val size=if frequency=="2min" then 2 else 5
          val time=LocalDateTime.parse(bar.date,timestamp)
          time.withMinute(time.getMinute-time.getMinute%size).withSecond(0).format(timestamp)
        case _=>throw new IllegalArgumentException("Unsupported frequency")
      }.toList.sortBy(_._1).map {case(date,rows)=>
        val sorted=rows.sortBy(_.date)
        DailyBar(date,sorted.head.open,rows.map(_.high).max,rows.map(_.low).min,sorted.last.close,rows.map(_.volume).sum,rows.map(_.minutes).sum)
      }
