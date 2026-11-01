package services.backtest.utils
import cats.effect.IO
import io.circe.Json
import services.system.http.ServiceClient
private[backtest] object Remote:
  def post(url:String,body:Json):IO[Json]=ServiceClient.postUrl(url,body)
