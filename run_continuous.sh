#!/bin/bash

cd `dirname $0`
# cd ..

clear

while true; do

  ./run_benchmark.py -p
  run_exit=$?
  echo "Run exit: $compiler_exit"

  xdotool search --name "Mozilla Firefox" key CTRL+r

  change=$(inotifywait -r -e close_write,moved_to,create,modify . \
    --exclude 'benchmarks|#.*' \
    2> /dev/null)

  # very short sleep to avoid "text file busy"
  sleep 0.01

  clear
  echo "changed: $change `date +%T`"
done
