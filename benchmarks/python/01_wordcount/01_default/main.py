#!/usr/bin/env python

from __future__ import print_function

import sys
import time
import re


if len(sys.argv) != 2:
    sys.exit(-1)


class TimedContext(object):

    def __enter__(self):
        self.t1 = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t2 = time.time()
        print(self.t2 - self.t1)


with TimedContext():
    f = open(sys.argv[1], "r")
    all_data = f.read()

with TimedContext():
    #words = all_data.split(" \n")
    words = re.split(" |\n", all_data)

with TimedContext():
    word_counts = dict()

    for w in words:
        word_counts[w] = word_counts.get(w, 0) + 1

print(len(word_counts))
word_checksum = 0
for w, c in word_counts.iteritems():
    word_checksum += c
print(word_checksum)
