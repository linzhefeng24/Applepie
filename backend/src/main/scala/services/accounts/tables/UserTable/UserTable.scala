package services.accounts.tables.UserTable
import cats.effect.IO
import java.sql.{Connection,ResultSet,SQLException}
import services.accounts.objects.StoredUser
import services.system.api.HttpError
object UserTable:
  private val columns="id::text,username,display_name,password_hash,credentials_version,bootstrap"
  private def row(r:ResultSet):StoredUser=StoredUser(r.getString(1),r.getString(2),r.getString(3),r.getString(4),r.getInt(5),r.getBoolean(6))
  private def find(c:Connection,sql:String,value:String):Option[StoredUser]=
    val s=c.prepareStatement(sql);try {s.setString(1,value);val r=s.executeQuery();try if r.next() then Some(row(r)) else None finally r.close()} finally s.close()
  def byName(c:Connection,name:String):IO[Option[StoredUser]]=IO.blocking(find(c,s"SELECT $columns FROM accounts.users WHERE username=?",name))
  def byId(c:Connection,id:String):IO[Option[StoredUser]]=IO.blocking(find(c,s"SELECT $columns FROM accounts.users WHERE id=?::uuid",id))
  def list(c:Connection):IO[List[StoredUser]]=IO.blocking {val s=c.createStatement();try {val r=s.executeQuery(s"SELECT $columns FROM accounts.users ORDER BY created_at");try Iterator.continually(r.next()).takeWhile(identity).map(_=>row(r)).toList finally r.close()} finally s.close()}
  def create(c:Connection,id:String,name:String,display:String,digest:String):IO[StoredUser]=IO.blocking {
    val lock=c.createStatement();try lock.execute("SELECT pg_advisory_xact_lock(1594101)") finally lock.close()
    val count=c.createStatement();val first=try {val r=count.executeQuery("SELECT count(*) FROM accounts.users");try {r.next();r.getLong(1)==0} finally r.close()} finally count.close()
    val s=c.prepareStatement("INSERT INTO accounts.users(id,username,display_name,password_hash,bootstrap) VALUES (?::uuid,?,?,?,?)")
    try {s.setString(1,id);s.setString(2,name);s.setString(3,display);s.setString(4,digest);s.setBoolean(5,first);s.executeUpdate();StoredUser(id,name,display,digest,1,first)}
    catch case e:SQLException if e.getSQLState=="23505"=>throw HttpError(409,"用户名已存在，请登录或使用其他用户名")
    finally s.close()
  }
  def changePassword(c:Connection,id:String,version:Int,digest:String):IO[Unit]=IO.blocking {
    val s=c.prepareStatement("UPDATE accounts.users SET password_hash=?,credentials_version=credentials_version+1 WHERE id=?::uuid AND credentials_version=?")
    try {s.setString(1,digest);s.setString(2,id);s.setInt(3,version);if s.executeUpdate()!=1 then throw HttpError(409,"凭据已被更新，请重新登录");()} finally s.close()
  }
  def updateDisplay(c:Connection,id:String,display:String):IO[Unit]=IO.blocking {val s=c.prepareStatement("UPDATE accounts.users SET display_name=? WHERE id=?::uuid");try {s.setString(1,display);s.setString(2,id);s.executeUpdate();()} finally s.close()}
