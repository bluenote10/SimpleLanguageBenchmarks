java -cp target/scala-2.11/benchmarkwordcount_2.11-1.0.jar:$(cat target/streams/compile/dependencyClasspath/\$global/streams/export) Main "$1"
#sbt run "$1"
