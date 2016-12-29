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


class SimpleMatrix(object):

    def __init__(self, N, data):
        self._data = data
        self._N = N

    def __add__(self, other):
        assert(self._N == other._N)
        N = self._N
        data = list(xrange(N*N))
        for i in xrange(N):
            for j in xrange(N):
                data[i*N+j] = self._data[i*N+j] + other._data[i*N+j]
        return SimpleMatrix(N, data)

    def __mul__(self, other):
        assert(self._N == other._N)
        N = self._N
        data = list(xrange(N*N))
        for i in xrange(N):
            for j in xrange(N):
                sum = 0
                for z in xrange(N):
                    sum += self._data[i*N+z] + other._data[z*N+j]
                data[i * N + j] = sum
        return SimpleMatrix(N, data)

    def diag_sum(self):
        sum = 0
        for i in xrange(self._N):
            sum += self._data[i*(N+1)]
        return sum


def load_from_data(N, csv_path):
    data = list(xrange(N * N))
    with open(csv_path) as f:
        for i, line in enumerate(f):
            values = line.split(";")
            for j, value in enumerate(values):
                data[i*N+j] = float(value)
    return SimpleMatrix(N, data)


if len(sys.argv) != 4:
    sys.exit(1)

N = int(sys.argv[1])
filename_mat_A = sys.argv[2]
filename_mat_B = sys.argv[3]

with TimedContext():
    m_A = load_from_data(N, filename_mat_A)
    m_B = load_from_data(N, filename_mat_B)

with TimedContext():
    m_add = m_A + m_B

with TimedContext():
    m_mul = m_A * m_B

print(m_add.diag_sum())
print(m_mul.diag_sum())
