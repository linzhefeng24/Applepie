package services.sessions.tables.SessionTable
import cats.effect.IO
import java.sql.Connection
import io.circe.Json
import io.circe.syntax.*
object SessionTable:
  def create(c:Connection,id:String,userId:String,hash:String,version:Int,expires:String):IO[Unit]=IO.blocking {
    val s=c.prepareStatement("INSERT INTO sessions.session(id,user_id,token_hash,credentials_version,expires_at) VALUES (?::uuid,?::uuid,?,?,?::timestamptz)")
    try {s.setString(1,id);s.setString(2,userId);s.setString(3,hash);s.setInt(4,version);s.setString(5,expires);s.executeUpdate();()} finally s.close()
  }
  def validate(c:Connection,hash:String):IO[Option[Json]]=IO.blocking {
    val s=c.prepareStatement("SELECT user_id::text,credentials_version FROM sessions.session WHERE token_hash=? AND revoked_at IS NULL AND expires_at>clock_timestamp()")
    try {s.setString(1,hash);val r=s.executeQuery();try if r.next() then Some(Json.obj("userId"->r.getString(1).asJson,"credentialsVersion"->r.getInt(2).asJson)) else None finally r.close()} finally s.close()
  }
  def list(c:Connection,userId:String,currentHash:String):IO[Json]=IO.blocking {
    val s=c.prepareStatement("SELECT id::text,created_at::text,expires_at::text,token_hash FROM sessions.session WHERE user_id=?::uuid AND revoked_at IS NULL AND expires_at>clock_timestamp() ORDER BY created_at DESC")
    try {s.setString(1,userId);val r=s.executeQuery();try Iterator.continually(r.next()).takeWhile(identity).map(_=>Json.obj("id"->r.getString(1).asJson,"createdAt"->r.getString(2).asJson,"expiresAt"->r.getString(3).asJson,"current"->(r.getString(4)==currentHash).asJson)).toList.asJson finally r.close()} finally s.close()
  }
  def revoke(c:Connection,userId:String,sessionId:Option[String],hash:Option[String]):IO[Unit]=IO.blocking {
    val sql="UPDATE sessions.session SET revoked_at=clock_timestamp() WHERE user_id=?::uuid"+sessionId.fold("")(_=>" AND id=?::uuid")+hash.fold("")(_=>" AND token_hash=?")
    val s=c.prepareStatement(sql)
    try {s.setString(1,userId);sessionId.orElse(hash).foreach(v=>s.setString(2,v));s.executeUpdate();()} finally s.close()
  }
