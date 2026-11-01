package services.history.objects.apiTypes
import io.circe.{Encoder,Decoder}
import io.circe.generic.semiauto.*
import services.history.objects.FrequencyOption
final case class ListFrequenciesResponse(symbol:String,frequencies:List[FrequencyOption],maxBars:Int,timezone:String)
object ListFrequenciesResponse:
  given Encoder[ListFrequenciesResponse]=deriveEncoder
  given Decoder[ListFrequenciesResponse]=deriveDecoder
