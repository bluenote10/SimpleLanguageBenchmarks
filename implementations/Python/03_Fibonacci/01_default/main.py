#!/usr/bin/env python

from __future__ import print_function

import sys
import time


class TimedContext(object):

    def __enter__(self):
        self.t1 = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t2 = time.time()
        print(self.t2 - self.t1)


def fibonacci_naive(N):
    if N < 2:
        return N
    else:
        return fibonacci_naive(N-1) + fibonacci_naive(N-2)


def fibonacci_tailrec(N, a=0, b=1):
    if N == 0:
        return a
    else:
        return fibonacci_tailrec(N-1, b, a+b)


def fibonacci_iterative(N):
    a = 0
    b = 1
    while N > 0:
        a, b = b, a + b
        N -= 1
    return a


if len(sys.argv) != 3:
    sys.exit(1)
N1 = int(sys.argv[1])
N2 = int(sys.argv[2])


# Note: Crashes without explicitly increasing recursion limit
sys.setrecursionlimit(N2*2)


with TimedContext():
    f1 = fibonacci_naive(N1)

with TimedContext():
    sum_f2 = 0
    for N in xrange(N2):
        sum_f2 += fibonacci_tailrec(N)

with TimedContext():
    sum_f3 = 0
    for N in xrange(N2):
        sum_f3 += fibonacci_iterative(N)

print(f1)
print(sum_f2)
print(sum_f3)
