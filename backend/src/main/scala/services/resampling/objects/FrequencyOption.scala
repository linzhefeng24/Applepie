package services.resampling.objects
import io.circe.{Encoder,Decoder}
import io.circe.generic.semiauto.*
final case class FrequencyOption(code:String,label:String,available:Boolean,start:String,end:String,observations:Long)
object FrequencyOption:
  given Encoder[FrequencyOption]=deriveEncoder
  given Decoder[FrequencyOption]=deriveDecoder
