package services.system
import cats.effect.{IO, Resource}
import java.sql.{Connection, DriverManager}
object Database:
  def connection: Resource[IO, Connection] =
    Resource.make(IO.blocking {
      val host = sys.env.getOrElse("DB_HOST", "127.0.0.1")
      val port = sys.env.getOrElse("DB_PORT", "55432")
      val name = sys.env.getOrElse("DB_NAME", "terminal")
      val c = DriverManager.getConnection(
        s"jdbc:postgresql://$host:$port/$name",
        sys.env.getOrElse("DB_USER", "terminal"),
        sys.env.getOrElse("DB_PASSWORD", "")
      )
      c.setAutoCommit(false)
      c
    })(c => IO.blocking(c.close()))
  def transaction[A](f: Connection => IO[A]): IO[A] =
    connection.use(c =>
      f(c).flatTap(_ => IO.blocking(c.commit())).onError(_ => IO.blocking(c.rollback()))
    )
