package services.quotes.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.StatelessMessage
import services.system.http.ServiceClient
import services.daily.objects.DailyBar
final case class ListQuotesMessage() extends StatelessMessage[Json]:
  def plan: IO[Json] =
    ServiceClient.post("daily","gettailbars",Json.obj()).map { json=>
      val series=json.hcursor.get[Map[String,List[DailyBar]]]("series").fold(throw _,identity)
      Json.obj("quotes"->Json.obj(series.toSeq.map {case(symbol,bars)=>
        val last=bars.last;val previous=bars.dropRight(1).lastOption.map(_.close).getOrElse(last.close)
        symbol->Json.obj("date"->last.date.asJson,"close"->last.close.asJson,"volume"->last.volume.asJson,"changePct"->(last.close/previous-1).asJson)
      }*))
    }
object ListQuotesMessage:
  given Decoder[ListQuotesMessage]=deriveDecoder
