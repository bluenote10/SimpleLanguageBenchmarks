import scala.io.Source


class SimpleMatrix(val N: Int, val data: Array[Double]) {
  
  def +(that: SimpleMatrix): SimpleMatrix = {
    val newData = Array.ofDim[Double](N * N)
    for (i <- Range(0, N)) {
      for (j <- Range(0, N)) {
        newData(i*N + j) = this.data(i*N + j) + that.data(i*N + j)
      }
    }
    new SimpleMatrix(N, newData)
  }
  
  def *(that: SimpleMatrix): SimpleMatrix = {
    val newData = Array.ofDim[Double](N * N)
    for (i <- Range(0, N)) {
      for (j <- Range(0, N)) {
        var sum = 0d
        for (k <- Range(0, N)) {
          sum += this.data(i*N + k) + that.data(k*N + j)
        }
        newData(i*N + j) = sum
      }
    }
    new SimpleMatrix(N, newData)
  }

  def diagSum(): Double = {
    var sum = 0d
    for (i <- Range(0, N)) {
      sum += data(i*(N+1))
    }
    sum
  }
  
}


object SimpleMatrix {
  
  def fromCsv(N: Int, filename: String): SimpleMatrix = {
    // Preallocating and iterating with explicit i, j indices
    // feels weird in Scala. Flatmapping is maybe more natural?
    val data = Source.fromFile(filename).getLines().flatMap { line =>
      line.split(";").map(_.toDouble)
    }
    new SimpleMatrix(N, data.toArray)
  }

}


object Main {
  
  def runTimed[T](body: => T): T = {
    val t1 = System.nanoTime()
    val res = body
    val t2 = System.nanoTime()
    println((t2 - t1).toDouble / 1000000000)
    res
  }
  
  def main(args: Array[String]): Unit = {
    
    if (args.length != 3) {
      System.exit(1)  
    }
    val N = args(0).toInt
    val filenameMatA = args(1)
    val filenameMatB = args(2)
    
    val (matA, matB) = runTimed{
      (SimpleMatrix.fromCsv(N, filenameMatA), SimpleMatrix.fromCsv(N, filenameMatA))
    }
    
    val matAdd = runTimed{
      matA + matB
    }
    
    val matMul = runTimed{
      matA * matB
    }
    
    println(matAdd.diagSum())
    println(matMul.diagSum())
  }
  
}