package services.reports.tables.ReportTable
import cats.effect.IO
import java.sql.Connection
import io.circe.Json
import io.circe.parser.parse
import services.reports.objects.ResearchReport
object ReportTable:
  private val listSql =
    "SELECT id::text,title,kind,created_at::text,parameters::text,result::text FROM reports.report WHERE user_id=?::uuid ORDER BY created_at DESC LIMIT 50"
  def list(connection: Connection,userId:String): IO[List[ResearchReport]] = IO.blocking {
    val s = connection.prepareStatement(listSql)
    try
      s.setString(1,userId);val r = s.executeQuery()
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
    "INSERT INTO reports.report(id,title,kind,parameters,result,user_id) VALUES (?::uuid,?,?,?::jsonb,?::jsonb,?::uuid)"
  def insert(
      connection: Connection,
      id: String,
      userId:String,
      title: String,
      kind: String,
      parameters: Json,
      result: Json
  ): IO[Unit] = IO.blocking {
    val s = connection.prepareStatement(insertSql)
    try {
      s.setString(1, id); s.setString(2, title); s.setString(3, kind);
      s.setString(4, parameters.noSpaces); s.setString(5, result.noSpaces);s.setString(6,userId); s.executeUpdate(); ()
    } finally s.close()
  }
  private val deleteSql = "DELETE FROM reports.report WHERE id=?::uuid AND user_id=?::uuid"
  def delete(connection: Connection, id: String,userId:String): IO[Unit] = IO.blocking {
    val s = connection.prepareStatement(deleteSql);
    try { s.setString(1, id);s.setString(2,userId); s.executeUpdate(); () }
    finally s.close()
  }
