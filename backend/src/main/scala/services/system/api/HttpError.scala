package services.system.api
final case class HttpError(status:Int,publicMessage:String) extends RuntimeException(publicMessage)
