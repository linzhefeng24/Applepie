package services.accounts.utils
import java.security.{MessageDigest,SecureRandom}
import java.util.Base64
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec
private[accounts] object PasswordHasher:
  private val random=new SecureRandom()
  private val encoder=Base64.getUrlEncoder.withoutPadding()
  private val decoder=Base64.getUrlDecoder
  private val iterations=310000
  private def derive(password:String,salt:Array[Byte],rounds:Int):Array[Byte]=
    val key=new PBEKeySpec(password.toCharArray,salt,rounds,256)
    try SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(key).getEncoded finally key.clearPassword()
  def validate(password:String):Unit=require(password.length>=10&&password.length<=128,"密码长度需为10–128个字符")
  def hash(password:String):String=
    validate(password);val salt=new Array[Byte](16);random.nextBytes(salt)
    s"pbkdf2-sha256$$$iterations$$${encoder.encodeToString(salt)}$$${encoder.encodeToString(derive(password,salt,iterations))}"
  def verify(password:String,stored:Option[String]):Boolean=
    val encoded=stored.getOrElse("pbkdf2-sha256$310000$AAAAAAAAAAAAAAAAAAAAAA$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    try
      val parts=encoded.split("\\$")
      val rounds=parts(1).toInt
      if parts.length!=4||parts(0)!="pbkdf2-sha256"||rounds<200000||rounds>1000000||password.length>128 then false
      else
        val actual=derive(password,decoder.decode(parts(2)),rounds)
        val matched=MessageDigest.isEqual(actual,decoder.decode(parts(3)))
        stored.nonEmpty&&matched
    catch
      case _:IllegalArgumentException=>false
      case _:IndexOutOfBoundsException=>false
