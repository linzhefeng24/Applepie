package services.resampling.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.resampling.api.*
object ResamplingRoutes:
  val apiMessages=List(
    register[GetBarsMessage,services.resampling.objects.apiTypes.GetBarsResponse](classOf[GetBarsMessage].getSimpleName,permission="data:read",ownerBound=false),
    register[ListFrequenciesMessage,services.resampling.objects.apiTypes.ListFrequenciesResponse](classOf[ListFrequenciesMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
