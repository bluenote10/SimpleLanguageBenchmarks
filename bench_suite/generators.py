#!/usr/bin/env python

from __future__ import print_function

import random
import string
import numpy as np


def random_word(length):
    return ''.join(random.choice(string.lowercase) for _ in xrange(length))


def generate_text(path, chars_to_write=100*1000*1000):

    num_words = 100000

    random_words = [random_word(random.randint(1, 20)) for _ in xrange(num_words)]

    with open(path, "w") as f:
        chars_written = 0
        chars_in_line = 0

        while chars_written < chars_to_write:
            w = random.choice(random_words)

            if chars_in_line == 0:
                f.write(w)
                chars_in_line += len(w)
                chars_written += len(w)

            elif chars_in_line + len(w) < 80:
                f.write(" " + w)
                chars_in_line += len(w) + 1
                chars_written += len(w) + 1

            else:
                f.write("\n" + w)
                chars_in_line = len(w)
                chars_written += len(w)


def generate_matrix(path, N):
    X = np.random.uniform(-1, 1, size=(N, N))
    np.savetxt(path, X, delimiter=";")

