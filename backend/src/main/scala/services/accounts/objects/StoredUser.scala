package services.accounts.objects
/** Private persistence shape; password digests are never serialized to HTTP. */
private[accounts] final case class StoredUser(id:String,username:String,displayName:String,passwordHash:String,credentialsVersion:Int,bootstrap:Boolean)
