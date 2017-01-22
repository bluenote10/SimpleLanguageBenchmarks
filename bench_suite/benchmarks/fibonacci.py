#!/usr/bin/env python

from __future__ import division, print_function

import textwrap
import os
import traceback

from ..base import *
from ..utils import *


class Fibonacci(object):

    title = "Fibonacci"

    description = textwrap.dedent("""\
    Compute the N-th Fibonacci using three different, popular implementations:

    - **Naive Recursion**: Version using the naive recursion (1 iteration).
    - **Tail Recursion**: Version using the tail recursion (M iterations).
    - **Iterative**: Iterative version using loops (M iterations).

    Each version will be run in a separate benchmark stage.
    In order to bring the tail-recursive and the iterative versions
    in a measurable range (if possible at all), the implementations have to
    repeat the computation M times, updating a checksum according to:

        checksum = 0
        for i in 0 .. <M:
            checksum += fibonacci_iterative(N)
            checksum %= 2147483647

    Benchmark aspects: Recursion

    <div class="page-header"></div>
    #### Input

    - N -- The Fibonacci number to compute.
    - M -- The number of iterations to repeat the tail-recursive and iterative implementations.

    <div class="page-header"></div>
    #### Control Output

    After writing the stage runtimes to STDOUT, the implementations should print:

    - N-th Fibonacci result (result from first stage)
    - checksum from second stage
    - checksum from third stage

    """)

    sizes = {
        Sizes.S: (34, int(1.45 ** 32)),
        Sizes.M: (36, int(1.45 ** 34)),
        Sizes.L: (38, int(1.45 ** 36)),
    }

    stages = ["Total", "Naive Recursion", "Tail Recursion", "Iterative"]

    linear_scales = {
        "Total": False,
        "Naive Recursion": False,
        "Tail Recursion": False,
        "Iterative": False,
    }

    @staticmethod
    def benchmark_args(size):
        return [str(N) for N in Fibonacci.sizes[size]]

    @staticmethod
    def ensure_data_exists():
        pass

    @staticmethod
    def result_extractor(b_entry):
        # TODO: rewrite finally...
        runtimes_io = []
        runtimes_split = []
        runtimes_count = []
        for size in Sizes:
            files = b_entry.result_files(size)
            for fn in files:
                with open(fn) as f:
                    try:
                        t1 = float(f.readline())
                        t2 = float(f.readline())
                        t3 = float(f.readline())
                        runtimes_io.append(t1)
                        runtimes_split.append(t2)
                        runtimes_count.append(t3)
                    except ValueError, e:
                        print(
                            AnsiColors.FAIL +
                            "Output did not fulfil expected format:" +
                            AnsiColors.ENDC
                        )
                        print(traceback.format_exc())

        N = len(runtimes_io)
        runtimes_total = [
            runtimes_io[i] + runtimes_split[i] + runtimes_count[i]
            for i in xrange(N)
        ]

        result = {
            "Total": runtimes_total,
            "Naive Recursion": runtimes_io,
            "Tail Recursion": runtimes_split,
            "Iterative": runtimes_count,
        }
        return result