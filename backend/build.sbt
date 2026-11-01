ThisBuild / scalaVersion := "3.3.3"
ThisBuild / version := "0.2.0"
lazy val dependencies = Seq(
  "org.typelevel" %% "cats-effect" % "3.5.4",
  "org.http4s" %% "http4s-ember-server" % "0.23.27",
  "org.http4s" %% "http4s-ember-client" % "0.23.27",
  "org.http4s" %% "http4s-dsl" % "0.23.27",
  "org.http4s" %% "http4s-circe" % "0.23.27",
  "io.circe" %% "circe-generic" % "0.14.9",
  "io.circe" %% "circe-parser" % "0.14.9",
  "org.postgresql" % "postgresql" % "42.7.4",
  "com.zaxxer" % "HikariCP" % "5.1.0"
)
lazy val contracts = project.in(file("modules/contracts")).settings(
  libraryDependencies ++= dependencies,
  Compile / unmanagedSources := ((ThisBuild / baseDirectory).value / "src/main/scala/services" ** "*.scala").get.filter(p => p.getPath.contains("/objects/") && p.getName != "StoredUser.scala")
)
lazy val platform = project.in(file("modules/platform")).dependsOn(contracts).settings(
  libraryDependencies ++= dependencies,
  Compile / unmanagedSources := ((ThisBuild / baseDirectory).value / "src/main/scala/services/system" ** "*.scala").get.filterNot(_.getPath.contains("/objects/"))
)
def service(id: String) = Project(id, file("modules/" + id)).dependsOn(platform, contracts).settings(
  name := "aperture-" + id,
  libraryDependencies ++= dependencies,
  Compile / unmanagedSources := ((ThisBuild / baseDirectory).value / ("src/main/scala/services/" + id) ** "*.scala").get.filter(p => !p.getPath.contains("/objects/") || p.getName == "StoredUser.scala"),
  Compile / mainClass := Some("services." + id + ".routes.ServiceMain")
)
lazy val catalog = service("catalog")
lazy val quotes = service("quotes")
lazy val provenance = service("provenance")
lazy val daily = service("daily")
lazy val minute = service("minute")
lazy val resampling = service("resampling")
lazy val statistics = service("statistics")
lazy val performance = service("performance")
lazy val risk = service("risk")
lazy val annual = service("annual")
lazy val watchlist = service("watchlist")
lazy val reports = service("reports")
lazy val optimization = service("optimization")
lazy val backtest = service("backtest")
lazy val accounts = service("accounts")
lazy val sessions = service("sessions")
lazy val authorization = service("authorization")
lazy val root = project.in(file(".")).aggregate(catalog,quotes,provenance,daily,minute,resampling,statistics,performance,risk,annual,watchlist,reports,optimization,backtest,accounts,sessions,authorization).settings(
  Compile / sources := Nil
)
