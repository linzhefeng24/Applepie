package services.system.security
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import org.http4s.Request
import cats.effect.IO
import io.circe.parser.parse
import org.typelevel.ci.CIString
object ServiceTrust:
  private val trusted=parse(sys.env.getOrElse("TRUSTED_SERVICE_HASHES","{}")).toOption.flatMap(_.as[Map[String,String]].toOption).getOrElse(Map.empty)
  private def header(request:Request[IO],name:String):String=request.headers.get(CIString(name)).map(_.head.value).getOrElse("")
  def caller(request:Request[IO]):Option[String]=
    val name=header(request,"X-Service-Name");val token=header(request,"X-Internal-Token")
    val digest=MessageDigest.getInstance("SHA-256").digest(token.getBytes(StandardCharsets.UTF_8)).map(b=>f"${b & 0xff}%02x").mkString
    trusted.get(name).filter(expected=>token.length>=32&&MessageDigest.isEqual(digest.getBytes(StandardCharsets.UTF_8),expected.getBytes(StandardCharsets.UTF_8))).map(_=>name)
