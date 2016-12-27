name := "BenchmarkWordcount"
version := "1.0"
scalaVersion := "2.11.8"
mainClass in (Compile, run) := Some("Main")

fork in run := true
outputStrategy := Some(StdoutOutput)

// javaOptions in run += "-DXmx8G"

