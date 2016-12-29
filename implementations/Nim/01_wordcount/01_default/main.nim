import os
import strutils
import tables
import times

if paramCount() != 1:
  echo "Wrong"
  quit(1)

var
  t1: float
  t2: float

let filename = paramStr(1)

# read
t1 = epochTime()
let content = readFile(filename)
t2 = epochTime()
echo t2 - t1

# split
t1 = epochTime()
let words = content.split({'\x0D', '\x0A', ' '})
t2 = epochTime()
echo t2 - t1

# count
t1 = epochTime()
var wordCounts = initTable[string, int]()
for w in words:
  wordCounts.mgetOrPut(w, 0) += 1
t2 = epochTime()
echo t2 - t1

# control output
echo wordCounts.len
var sum = 0
for w, count in wordCounts.pairs():
  sum += count
echo sum
