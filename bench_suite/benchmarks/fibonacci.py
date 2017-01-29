#!/usr/bin/env python

from __future__ import division, print_function

import textwrap

from ..base import Sizes, default_runtime_extractor


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

    After writing the stage run times to STDOUT, the implementations should print:

    - N-th Fibonacci result (result from first stage)
    - checksum from second stage
    - checksum from third stage

    """)

    sizes = {
        Sizes.S: (34, int(1.45 ** 32)),
        Sizes.M: (36, int(1.45 ** 34)),
        Sizes.L: (38, int(1.45 ** 36)),
    }

    @classmethod
    def size_description(cls, size):
        return "N = {}, M = {}".format(*cls.sizes[size])

    stages = ["Total", "Naive Recursion", "Tail Recursion", "Iterative"]

    linear_scales = {
        "Total": False,
        "Naive Recursion": False,
        "Tail Recursion": False,
        "Iterative": False,
    }

    @classmethod
    def benchmark_args(cls, size):
        return [str(N) for N in cls.sizes[size]]

    @classmethod
    def ensure_data_exists(cls):
        pass

    @classmethod
    def result_extractor(cls, b_entry):
        result = default_runtime_extractor(
            b_entry,
            cls.stages[1:],
            add_total_stage=True
        )
        return result

