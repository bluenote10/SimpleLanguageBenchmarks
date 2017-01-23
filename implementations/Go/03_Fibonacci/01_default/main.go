package main

import (
    "fmt"
    "os"
    "strconv"
    "time"
)

func fibonacci_naive(a int) int {
    if a < 2 {
        return a
    }
    return fibonacci_naive(a - 1) + fibonacci_naive(a - 2)
}

func fibonacci_tailrec(N int, a int, b int) int {
    if N == 0 {
        return a
    } else {
        return fibonacci_tailrec(N-1, b, a+b)
    }
}

func fibonacci_iterative(N int) int {
    a := 0
    b := 1
    for N > 0 {
        a, b = b, a+b
        N -= 1
    }
    return a
}

func main() {
    if len(os.Args) != 3 {
        os.Exit(1)
    }
    N, _ := strconv.Atoi(os.Args[1])
    M, _ := strconv.Atoi(os.Args[2])

    start1 := time.Now()
    f1 := fibonacci_naive(N)
    t1 := time.Since(start1)

    start2 := time.Now()
    checksum_f2 := 0
    for i := 0; i < M; i++ {
		    checksum_f2 += fibonacci_tailrec(N, 0, 1)
        checksum_f2 = checksum_f2 % 2147483647
	  }
    t2 := time.Since(start2)

    start3 := time.Now()
    checksum_f3 := 0
    for i := 0; i < M; i++ {
		    checksum_f3 += fibonacci_iterative(N)
        checksum_f3 = checksum_f2 % 2147483647
	  }
    t3 := time.Since(start3)

    fmt.Println(t1.Seconds())
    fmt.Println(t2.Seconds())
    fmt.Println(t3.Seconds())

    fmt.Println(f1)
    fmt.Println(checksum_f2)
    fmt.Println(checksum_f3)
}