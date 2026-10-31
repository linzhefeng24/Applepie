package services.system.api
import cats.effect.IO
import io.circe.Json
/** Platform registration metadata; it carries an IO plan, not a serialized domain record. */
final case class APIRegistration(name: String, execute: Json => IO[Json])
