package services.system.api
import cats.effect.IO
import io.circe.Json
final case class APIRegistration(name:String,execute:Json=>IO[Json],permission:String="data:read",ownerBound:Boolean=false,withSession:Boolean=false,issueCookie:Boolean=false,clearCookie:Boolean=false,internalOnly:Boolean=false,callers:Set[String]=Set.empty)
