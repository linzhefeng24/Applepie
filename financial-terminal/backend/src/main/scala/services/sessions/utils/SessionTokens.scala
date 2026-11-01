package services.sessions.utils
import java.security.{MessageDigest,SecureRandom}
import java.nio.charset.StandardCharsets
import java.util.Base64
private[sessions] object SessionTokens:
  private val random=new SecureRandom()
  def create():String={val bytes=new Array[Byte](32);random.nextBytes(bytes);Base64.getUrlEncoder.withoutPadding().encodeToString(bytes)}
  def hash(token:String):String=MessageDigest.getInstance("SHA-256").digest(token.getBytes(StandardCharsets.UTF_8)).map(b=>f"${b & 0xff}%02x").mkString
