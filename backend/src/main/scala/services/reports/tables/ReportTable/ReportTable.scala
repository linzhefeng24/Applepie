package services.reports.tables.ReportTable
import cats.effect.IO
import java.sql.Connection
import io.circe.Json
import io.circe.parser.parse
import services.reports.objects.ResearchReport
object ReportTable:
  private val listSql =
    "SELECT id::text,title,kind,created_at::text,parameters::text,result::text FROM portfolio.report ORDER BY created_at DESC LIMIT 50"
  def list(connection: Connection): IO[List[ResearchReport]] = IO.blocking {
    val s = connection.prepareStatement(listSql)
    try
      val r = s.executeQuery()
      try
        Iterator
          .continually(r.next())
          .takeWhile(identity)
          .map(_ =>
            ResearchReport(
              r.getString(1),
              r.getString(2),
              r.getString(3),
              r.getString(4),
              parse(r.getString(5)).fold(throw _, identity),
              parse(r.getString(6)).fold(throw _, identity)
            )
          )
          .toList
      finally r.close()
    finally s.close()
  }
  private val insertSql =
    "INSERT INTO portfolio.report(id,title,kind,parameters,result) VALUES (?::uuid,?,?,?::jsonb,?::jsonb)"
  def insert(
      connection: Connection,
      id: String,
      title: String,
      kind: String,
      parameters: Json,
      result: Json
  ): IO[Unit] = IO.blocking {
    val s = connection.prepareStatement(insertSql)
    try {
      s.setString(1, id); s.setString(2, title); s.setString(3, kind);
      s.setString(4, parameters.noSpaces); s.setString(5, result.noSpaces); s.executeUpdate(); ()
    } finally s.close()
  }
  private val deleteSql = "DELETE FROM portfolio.report WHERE id=?::uuid"
  def delete(connection: Connection, id: String): IO[Unit] = IO.blocking {
    val s = connection.prepareStatement(deleteSql);
    try { s.setString(1, id); s.executeUpdate(); () }
    finally s.close()
  }
