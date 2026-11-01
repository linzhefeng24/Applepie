package services.authorization.utils
private[authorization] object Permissions:
  val read=List("data:read","profile:self","watchlist:read","reports:read","sessions:self")
  def forRole(role:String):List[String]=role match
    case "viewer"=>read
    case "analyst"=>read++List("research:compute","watchlist:write","reports:write")
    case "admin"=>read++List("research:compute","watchlist:write","reports:write","users:manage")
    case _=>Nil
