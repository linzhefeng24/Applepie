package services.analysis.objects
import io.circe.{Decoder, Encoder}
import io.circe.generic.semiauto.*
final case class AnalysisParameters(
    symbols: List[String],
    start: String,
    end: String,
    maxWeight: Double,
    riskAversion: Double,
    skewPreference: Double,
    kurtosisAversion: Double,
    lookback: Int,
    rebalance: Int,
    costBps: Double,
    model: String
)
object AnalysisParameters:
  given Decoder[AnalysisParameters] = deriveDecoder
  given Encoder[AnalysisParameters] = deriveEncoder
