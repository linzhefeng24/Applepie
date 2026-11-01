package services.accounts.utils
import java.util.concurrent.ConcurrentHashMap
import services.system.api.HttpError
private[accounts] object LoginLimiter:
  private val attempts=new ConcurrentHashMap[String,(Long,Int)]()
  def check(username:String):Unit=
    val now=System.currentTimeMillis()
    val state=attempts.compute(username,(_,old)=>if old==null||now-old._1>900000 then (now,1) else (old._1,old._2+1))
    if attempts.size()>10000 then attempts.entrySet().removeIf(entry=>now-entry.getValue._1>900000)
    if state._2>20 then throw HttpError(429,"登录尝试过多，请稍后再试")
  def clear(username:String):Unit={attempts.remove(username);()}
