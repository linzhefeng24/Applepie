package services.provenance.routes
import io.circe.Json
import services.system.api.APIMessageRouter.{register,registerInternal}
import services.provenance.api.*
object ProvenanceRoutes:
  val apiMessages=List(
    register[GetProvenanceMessage,Json](classOf[GetProvenanceMessage].getSimpleName,permission="data:read",ownerBound=false)
  )
