import os
import times
import strutils
import sequtils
import future
import tables

# template to simplify timed execution
template runTimed(body: untyped) =
  let t1 = epochTime()
  body
  let t2 = epochTime()
  echo t2 - t1

# parameter validation
if paramCount() != 2:
  quit(1)
let N = paramStr(1).parseInt
let M = paramStr(2).parseInt


proc fibonacci_naive(N: int): int64 =
  if N < 2:
    result = N
  else:
    result = fibonacci_naive(N-1) + fibonacci_naive(N-2)

proc fibonacci_tailrec(N: int, a: int64 = 0, b: int64 = 1): int64 =
  if N == 0:
    result = a
  else:
    result = fibonacci_tailrec(N-1, b, a+b)

proc fibonacci_iterative(N: int): int64 =
  var (a, b) = (0.int64, 1.int64)
  var Ncopy = N
  while Ncopy > 0:
    (a, b) = (b, a+b)
    Ncopy -= 1
  result = a


runTimed:
  let f1 = fibonacci_naive(N)

runTimed:
  var checksum_f2 = 0.int64
  for i in 0 .. <M:
    checksum_f2 += fibonacci_tailrec(N)
    checksum_f2 = checksum_f2 %% 2147483647

runTimed:
  var checksum_f3 = 0.int64
  for i in 0 .. <M:
    checksum_f3 += fibonacci_iterative(N)
    checksum_f3 = checksum_f3 %% 2147483647

echo f1
echo checksum_f2
echo checksum_f3
