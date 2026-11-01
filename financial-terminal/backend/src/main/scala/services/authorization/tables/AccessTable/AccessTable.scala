package services.authorization.tables.AccessTable
import cats.effect.IO
import java.sql.Connection
import services.system.api.HttpError
object AccessTable:
  def ensure(c:Connection,userId:String,bootstrap:Boolean):IO[Unit]=IO.blocking {
    val s=c.prepareStatement("INSERT INTO access_control.access(user_id,role) VALUES (?::uuid,?) ON CONFLICT DO NOTHING")
    try {s.setString(1,userId);s.setString(2,if bootstrap then "admin" else "analyst");s.executeUpdate();()} finally s.close()
  }
  def get(c:Connection,userId:String):IO[Option[(String,Boolean)]]=IO.blocking {
    val s=c.prepareStatement("SELECT role,enabled FROM access_control.access WHERE user_id=?::uuid")
    try {s.setString(1,userId);val r=s.executeQuery();try if r.next() then Some((r.getString(1),r.getBoolean(2))) else None finally r.close()} finally s.close()
  }
  def all(c:Connection):IO[Map[String,(String,Boolean)]]=IO.blocking {
    val s=c.createStatement();try {val r=s.executeQuery("SELECT user_id::text,role,enabled FROM access_control.access");try Iterator.continually(r.next()).takeWhile(identity).map(_=>r.getString(1)->(r.getString(2),r.getBoolean(3))).toMap finally r.close()} finally s.close()
  }
  def set(c:Connection,userId:String,role:String,enabled:Boolean):IO[Unit]=IO.blocking {
    require(Set("admin","analyst","viewer").contains(role),"不支持的角色")
    val lock=c.createStatement();try lock.execute("SELECT pg_advisory_xact_lock(1594102)") finally lock.close()
    val s=c.prepareStatement("SELECT role,enabled,(SELECT count(*) FROM access_control.access WHERE role='admin' AND enabled) FROM access_control.access WHERE user_id=?::uuid FOR UPDATE")
    try {s.setString(1,userId);val r=s.executeQuery();try {
      if !r.next() then throw HttpError(404,"账户权限记录不存在")
      if r.getString(1)=="admin"&&r.getBoolean(2)&&r.getLong(3)<=1&&(role!="admin"|| !enabled) then throw HttpError(400,"不能移除最后一个有效管理员")
    } finally r.close()} finally s.close()
    val update=c.prepareStatement("UPDATE access_control.access SET role=?,enabled=? WHERE user_id=?::uuid")
    try {update.setString(1,role);update.setBoolean(2,enabled);update.setString(3,userId);update.executeUpdate();()} finally update.close()
  }
