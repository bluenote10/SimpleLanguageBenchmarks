#!/usr/bin/env python

from __future__ import division, print_function

import textwrap
import os
import traceback

from ..base import *
from ..utils import *
from .. import generators


class BasicMatOps(object):

    title = "Basic Matrix Operations"

    description = textwrap.dedent("""\
    Implement a basic matrix data structure providing addition and multiplication. Rules:

    - Default implementations should implement a matrix-like data structure backed by
      the native dynamic array of each language.
    - Additional implementations may make use of optimized matrix libraries.
    - Required operations: Matrix addition and multiplication.

    The benchmark is divided into three stages:

    - **IO**: Read two CSVs and construct matrices
    - **Add**: Add matrices
    - **Multiply**: Multiply matrices

    Benchmark aspects: Dynamic arrays, indexing, nested loops, code elegance of matrix implementations

    <div class="page-header"></div>
    #### Input

    1. Argument: Size N of the NxN matrix (allowing to pre-allocate required memory
       for the matrix; validation of CSV not necessary)
    2. Argument: Path of CSV (first matrix)
    3. Argument: Path of CSV (second matrix)

    Note: The framework may pass the same path as both first and second matrix.
    This must not be exploited, i.e., each matrix should still be read individually.

    <div class="page-header"></div>
    #### Control Output

    After writing the stage runtimes to STDOUT, the implementations should print:

    - Sum of diagonal elements after addition
    - Sum of diagonal elements after multiplication

    """)

    _datafile = {
        Sizes.S: os.path.abspath("data/generated/matrix_S.txt"),
        Sizes.M: os.path.abspath("data/generated/matrix_M.txt"),
        Sizes.L: os.path.abspath("data/generated/matrix_L.txt"),
    }

    sizes = {
        Sizes.S: 100,
        Sizes.M: 300,
        Sizes.L: 500,
    }

    stages = ["Total", "IO", "Add", "Mul"]

    linear_scales = {
        "Total": False,
        "IO": False,
        "Add": False,
        "Mul": False,
    }

    @staticmethod
    def benchmark_args(size):
        return [
            str(BasicMatOps.sizes[size]),
            BasicMatOps._datafile[size],
            BasicMatOps._datafile[size],
        ]

    @staticmethod
    def ensure_data_exists():
        for size, f in BasicMatOps._datafile.iteritems():
            if not os.path.exists(f):
                print_warn(
                    " *** Generating data [{}], this might take a while...".format(f)
                )
                generators.generate_matrix(f, BasicMatOps.sizes[size])

    @staticmethod
    def result_extractor(b_entry):
        # TODO: should we do the result validation here (when collecting the runtimes,
        # TODO: better name would probably be "extract_runtimes") or should there be
        # TODO: a separate "result_validator"? Probably the latter...
        runtimes_io = []
        runtimes_add = []
        runtimes_mul = []
        for size in Sizes:
            files = b_entry.result_files(size)
            for fn in files:
                with open(fn) as f:
                    try:
                        t1 = float(f.readline())
                        t2 = float(f.readline())
                        t3 = float(f.readline())
                        runtimes_io.append(t1)
                        runtimes_add.append(t2)
                        runtimes_mul.append(t3)
                    except ValueError, e:
                        print(
                            AnsiColors.FAIL +
                            "Output did not fulfil expected format:" +
                            AnsiColors.ENDC
                        )
                        print(traceback.format_exc())

        N = len(runtimes_io)
        runtimes_total = [
            runtimes_io[i] + runtimes_add[i] + runtimes_mul[i]
            for i in xrange(N)
        ]

        result = {
            "Total": runtimes_total,
            "IO": runtimes_io,
            "Add": runtimes_add,
            "Mul": runtimes_mul,
        }
        return result

