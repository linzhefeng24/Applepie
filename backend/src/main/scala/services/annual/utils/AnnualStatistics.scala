package services.annual.utils
import io.circe.Json
import io.circe.syntax.*
import services.daily.objects.DailyBar
import services.system.analytics.ReturnMath
private[annual] object AnnualStatistics:
  def annual(bars: List[DailyBar]): Json =
    val years = bars.groupBy(_.date.take(4)).toList.sortBy(_._1)
    years.map { (year, ys) =>
      val prior = bars.takeWhile(_.date < ys.head.date).lastOption.toList
      val metrics = ReturnMath.summary(prior ++ ys)
      metrics.deepMerge(
        Json.obj(
          "year" -> year.asJson,
          "sessions" -> ys.size.asJson,
          "volume" -> ys.map(_.volume).sum.asJson,
          "open" -> ys.head.open.asJson,
          "close" -> ys.last.close.asJson,
          "partial" -> (ys.size < 240).asJson
        )
      )
    }.asJson
