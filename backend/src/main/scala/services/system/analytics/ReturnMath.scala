package services.system.analytics
import io.circe.Json
import io.circe.syntax.*
import services.daily.objects.DailyBar
object ReturnMath:
  private def mean(xs: List[Double]): Double = if xs.isEmpty then 0.0 else xs.sum / xs.size
  def summary(bars: List[DailyBar]): Json =
    val returns = bars.sliding(2).collect { case List(a, b) => b.close / a.close - 1.0 }.toList
    val mu = mean(returns)
    val variance =
      if returns.size < 2 then 0.0
      else returns.map(r => math.pow(r - mu, 2)).sum / (returns.size - 1)
    val sd = math.sqrt(variance)
    val m2 = mean(returns.map(r => math.pow(r - mu, 2)))
    val skew =
      if m2 == 0 then 0.0 else mean(returns.map(r => math.pow(r - mu, 3))) / math.pow(m2, 1.5)
    val kurt = if m2 == 0 then 0.0 else mean(returns.map(r => math.pow(r - mu, 4))) / (m2 * m2) - 3
    val equity = bars.headOption.map(first => bars.map(_.close / first.close)).getOrElse(Nil)
    val peaks = equity.scanLeft(1.0)(math.max).tail
    val dd = equity.zip(peaks).map((e, p) => e / p - 1).minOption.getOrElse(0.0)
    val total = equity.lastOption.getOrElse(1.0) - 1
    Json.obj(
      "observations" -> returns.size.asJson,
      "totalReturn" -> total.asJson,
      "annualReturn" -> (if returns.isEmpty then 0.0
                         else math.pow(1 + total, 252.0 / returns.size) - 1).asJson,
      "volatility" -> (sd * math.sqrt(252)).asJson,
      "sharpe" -> (if sd == 0 then 0.0 else mu / sd * math.sqrt(252)).asJson,
      "maxDrawdown" -> dd.asJson,
      "mean" -> mu.asJson,
      "variance" -> variance.asJson,
      "skewness" -> skew.asJson,
      "excessKurtosis" -> kurt.asJson
    )
