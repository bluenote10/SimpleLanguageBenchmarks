#!/usr/bin/env python

from __future__ import print_function

import sys
import time
import os
import random
import string
import gzip


num_words = 100000
chars_to_write = 10000000


def random_word(length):
    return ''.join(random.choice(string.lowercase) for _ in xrange(length))

random_words = [random_word(random.randint(1, 20)) for _ in xrange(num_words)]

os.chdir(os.path.dirname(os.path.abspath(__file__)))
f = gzip.open("generated/random_words.txt.gz", "w")
chars_written = 0
chars_in_line = 0

while chars_written < chars_to_write:
    w = random.choice(random_words)

    if chars_in_line == 0:
        f.write(w)
        chars_in_line += len(w)
    elif chars_in_line + len(w) < 80:
        f.write(" " + w)
        chars_in_line += len(w)
    else:
        f.write("\n" + w)
        chars_in_line = 0

    chars_written += len(w)



