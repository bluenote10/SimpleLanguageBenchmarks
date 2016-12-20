
import scala.io.Source

class Stopwatch {
  var timeOld = System.nanoTime()
  
  def step() {
    val timeNew = System.nanoTime()
    println((timeNew - timeOld).toDouble / 1000000000)
    timeOld = timeNew
  }
}

object Main {
  
  def main(args: Array[String]): Unit = {
    
    if (args.length != 1) {
      System.exit(-1)  
    }
    val stopwatch = new Stopwatch
    
    val content = Source.fromFile(args(0)).mkString
    stopwatch.step()
    
    val words = content.split(Array(' ', '\n'))
    stopwatch.step()
    
    val counts = collection.mutable.Map[String, Int]()
    for (w <- words) {
      counts(w) = counts.getOrElse(w, 0) + 1
    }
    stopwatch.step()
    
    println(counts.size)
    println(counts.map(_._2).reduce(_ + _))
  }
  
}