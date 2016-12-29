import os
import strutils
import tables
import times

if paramCount() != 1:
  echo "Wrong"
  quit(1)
let filename = paramStr(1)

# template to simplify timed execution
template runTimed(body: untyped) =
  let t1 = epochTime()
  body
  let t2 = epochTime()
  echo t2 - t1

# read
runTimed:
  let content = readFile(filename)

# split
runTimed:
  let words = content.split({'\x0D', '\x0A', ' '})

# count
runTimed:
  var wordCounts = initTable[string, int]()
  for w in words:
    wordCounts.mgetOrPut(w, 0) += 1

# control output
echo wordCounts.len
var sum = 0
for w, count in wordCounts.pairs():
  sum += count
echo sum
