package services.resampling.objects.apiTypes
import io.circe.{Encoder,Decoder}
import io.circe.generic.semiauto.*
import services.daily.objects.DailyBar
final case class GetBarsResponse(symbol:String,frequency:String,sourceResolution:String,bars:List[DailyBar],queryStart:String,queryEnd:String,incompleteBars:Int)
object GetBarsResponse:
  given Encoder[GetBarsResponse]=deriveEncoder
  given Decoder[GetBarsResponse]=deriveDecoder
