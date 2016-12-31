#!/usr/bin/env python

from __future__ import print_function

import sys
import time
import numpy as np


class TimedContext(object):

    def __enter__(self):
        self.t1 = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t2 = time.time()
        print(self.t2 - self.t1)


if len(sys.argv) != 4:
    sys.exit(1)

N = int(sys.argv[1])
filename_mat_A = sys.argv[2]
filename_mat_B = sys.argv[3]

with TimedContext():
    m_A = np.loadtxt(filename_mat_A, delimiter=';')
    m_B = np.loadtxt(filename_mat_B, delimiter=';')

with TimedContext():
    m_add = m_A + m_B

with TimedContext():
    m_mul = np.dot(m_A, m_B)

print(np.trace(m_add))
print(np.trace(m_mul))
