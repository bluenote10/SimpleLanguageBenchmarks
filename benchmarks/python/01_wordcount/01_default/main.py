#!/usr/bin/env python

from __future__ import print_function

import sys
import time
import re
import gzip


class TimedContext(object):

    def __enter__(self):
        self.t1 = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t2 = time.time()
        print(self.t2 - self.t1)


with TimedContext():
    f = gzip.open(sys.argv[1], "r")
    all_data = f.read()

with TimedContext():
    #words = all_data.split(" \n")
    words = re.split(" |\n", all_data)

with TimedContext():
    word_counts = dict()

    for w in words:
        word_counts[w] = word_counts.get(w, 0) + 1

#for w, c in word_counts.iteritems():
#    print(w, c)