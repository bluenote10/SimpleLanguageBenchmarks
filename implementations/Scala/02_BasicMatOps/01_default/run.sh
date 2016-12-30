java -cp target/scala-2.11/benchmarkbasicmatops_2.11-1.0.jar:$(cat target/streams/compile/dependencyClasspath/\$global/streams/export) Main "$@"
#sbt run "$1"
