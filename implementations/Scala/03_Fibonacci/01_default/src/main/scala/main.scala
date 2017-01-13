
object Main {

  def runTimed[T](body: => T): T = {
    val t1 = System.nanoTime()
    val res = body
    val t2 = System.nanoTime()
    println((t2 - t1).toDouble / 1000000000)
    res
  }

  def fibonacciNaive(N: Int): Long = {
    if (N < 2) {
      N
    } else {
      fibonacciNaive(N-1) + fibonacciNaive(N-2)
    }
  }

  def fibonacciTailRec(N: Int, a: Long = 0, b: Long = 1): Long = {
    if (N == 0) {
      a
    } else {
      fibonacciTailRec(N-1, b, a+b)
    }
  }

  def fibonacciIterative(N: Int): Long = {
    var a = 0L
    var b = 1L
    var Ncopy = N
    while (Ncopy > 0) {
      val tmp = a
      a = b
      b = b + tmp
      Ncopy -= 1
    }
    a
  }

  def main(args: Array[String]): Unit = {

    if (args.length != 2) {
      System.exit(1)
    }
    val N = args(0).toInt
    val M = args(0).toInt

    val f1 = runTimed{
      fibonacciNaive(N)
    }

    val checksumF2 = runTimed{
      var checksum = 0L
      for (i <- 0 until M) {
        checksum += fibonacciTailRec(N)
        checksum %= 2147483647
      }
      checksum
    }

    val checksumF3 = runTimed{
      var checksum = 0L
      for (i <- 0 until M) {
        checksum += fibonacciIterative(N)
        checksum %= 2147483647
      }
      checksum
    }

    println(f1)
    println(checksumF2)
    println(checksumF3)
  }

}