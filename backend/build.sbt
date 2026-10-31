ThisBuild / scalaVersion := "3.3.3"
ThisBuild / version := "0.1.0"
lazy val root = (project in file(".")).settings(
  name := "financial-terminal-services",
  libraryDependencies ++= Seq(
    "org.typelevel" %% "cats-effect" % "3.5.4",
    "org.http4s" %% "http4s-ember-server" % "0.23.27",
    "org.http4s" %% "http4s-ember-client" % "0.23.27",
    "org.http4s" %% "http4s-dsl" % "0.23.27",
    "org.http4s" %% "http4s-circe" % "0.23.27",
    "io.circe" %% "circe-generic" % "0.14.9",
    "io.circe" %% "circe-parser" % "0.14.9",
    "org.postgresql" % "postgresql" % "42.7.4"
  ),
  Compile / mainClass := Some("Main"),
  Compile / run / fork := true
)
