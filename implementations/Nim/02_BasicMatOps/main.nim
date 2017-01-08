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
if paramCount() != 3:
  quit(1)
let N = paramStr(1).parseInt
let filenameMatA = paramStr(2)
let filenameMatB = paramStr(3)

# define matrix type
type
  Matrix = object
    N: int
    data: seq[float]

proc `+`(a, b: Matrix): Matrix =
  let N = a.N
  result.N = N
  result.data = newSeq[float](N * N)
  for i in 0 .. <result.data.len:
    result.data[i] = a.data[i] + b.data[i]

proc `*`(a, b: Matrix): Matrix =
  let N = a.N
  result.N = N
  result.data = newSeq[float](N * N)
  for i in 0 .. <N:
    for j in 0 .. <N:
      var sum = 0.0
      for k in 0 .. <N:
        sum += a.data[i*N+k] * b.data[k*N+j]
      result.data[i*N+j] = sum

proc trace(m: Matrix): float =
  result = 0
  for i in 0 .. <m.N:
    result += m.data[i*(N+1)]

proc loadFromCsv(N: int, filename: string): Matrix =
  var i = 0
  var data = newSeq[float](N*N)
  for line in lines filename:
    let values = line.split(';').map(x => x.parseFloat)
    for j in 0 .. <values.len:
      data[i*N+j] = values[j]
    i += 1
  result = Matrix(N: N, data: data)

# read
runTimed:
  let matA = loadFromCsv(N, filenameMatA)
  let matB = loadFromCsv(N, filenameMatB)

runTimed:
  let matAdd = matA + matB

runTimed:
  let matMul = matA * matB

echo matAdd.trace
echo matMul.trace
