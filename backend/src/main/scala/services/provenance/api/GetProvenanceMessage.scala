package services.provenance.api
import cats.effect.IO
import io.circe.{Decoder,Json}
import io.circe.generic.semiauto.*
import io.circe.syntax.*
import java.sql.Connection
import services.system.api.StatelessMessage

final case class GetProvenanceMessage() extends StatelessMessage[Json]:
  def plan: IO[Json] =
    IO.blocking(java.nio.file.Files.readString(java.nio.file.Path.of(sys.env("DATA_DIR"),"provenance.json"))).flatMap(s=>IO.fromEither(io.circe.parser.parse(s)))
object GetProvenanceMessage:
  given Decoder[GetProvenanceMessage]=deriveDecoder
