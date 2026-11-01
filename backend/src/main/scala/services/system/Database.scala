package services.system
import cats.effect.{IO,Resource}
import cats.syntax.all.*
import com.zaxxer.hikari.{HikariConfig,HikariDataSource}
import java.sql.Connection
import java.util.concurrent.atomic.AtomicReference
object Database:
  private val source=new AtomicReference[HikariDataSource]()
  val resource:Resource[IO,Unit]=
    if sys.env.getOrElse("DATABASE_REQUIRED","false")!="true" then Resource.pure[IO,Unit](())
    else Resource.make(IO.blocking {
      val cfg=new HikariConfig()
      cfg.setJdbcUrl(s"jdbc:postgresql://${sys.env("DB_HOST")}:${sys.env("DB_PORT")}/${sys.env("DB_NAME")}")
      cfg.setUsername(sys.env("DB_USER"));cfg.setPassword(sys.env("DB_PASSWORD"))
      cfg.setMaximumPoolSize(4);cfg.setMinimumIdle(0);cfg.setConnectionTimeout(10000);cfg.setAutoCommit(false)
      val ds=new HikariDataSource(cfg);source.set(ds);ds
    })(ds=>IO.blocking{source.set(null);ds.close()}).void
  def connection:Resource[IO,Connection]=Resource.make(IO.blocking {
    val ds=Option(source.get()).getOrElse(throw new IllegalStateException("This service has no database"))
    ds.getConnection()
  })(c=>IO.blocking(c.close()))
  def transaction[A](f:Connection=>IO[A]):IO[A]=connection.use(c=>f(c).flatTap(_=>IO.blocking(c.commit())).onError(_=>IO.blocking(c.rollback())))
  def ping:IO[Unit]=if sys.env.getOrElse("DATABASE_REQUIRED","false")!="true" then IO.unit else transaction { c=>IO.blocking {
    val statement=c.createStatement();try {val result=statement.executeQuery("SELECT 1");try {require(result.next());()} finally result.close()} finally statement.close()
  }}
