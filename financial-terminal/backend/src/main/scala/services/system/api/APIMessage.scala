package services.system.api
import cats.effect.IO
import java.sql.Connection
import services.system.Database
trait APIMessage[A]:
  def plan(connection: Connection): IO[A]
  def execute: IO[A] = Database.transaction(plan)
trait NoRequestMessage[A] extends APIMessage[A]
/** An explicitly stateless plan never acquires a dummy JDBC connection. */
trait ComposedMessage[A] extends APIMessage[A]:
  def plan: IO[A]
  final def plan(connection: Connection): IO[A] = plan
  final override def execute: IO[A] = plan

trait StatelessMessage[A] extends ComposedMessage[A]
