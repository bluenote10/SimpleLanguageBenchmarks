#!/usr/bin/env python

from __future__ import division, print_function

import textwrap
import os

from ..base import Sizes, default_runtime_extractor
from ..utils import print_warn
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

    After writing the stage run times to STDOUT, the implementations should print:

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

    @classmethod
    def size_description(cls, size):
        return "N = {}".format(cls.sizes[size])

    stages = ["Total", "IO", "Add", "Mul"]

    linear_scales = {
        "Total": False,
        "IO": False,
        "Add": False,
        "Mul": False,
    }

    @classmethod
    def benchmark_args(cls, size):
        return [
            str(cls.sizes[size]),
            cls._datafile[size],
            cls._datafile[size],
        ]

    @classmethod
    def ensure_data_exists(cls):
        for size, f in cls._datafile.iteritems():
            if not os.path.exists(f):
                print_warn(
                    " *** Generating data [{}], this might take a while...".format(f)
                )
                generators.generate_matrix(f, cls.sizes[size])

    @classmethod
    def result_extractor(cls, b_entry):
        result = default_runtime_extractor(
            b_entry,
            cls.stages[1:],
            add_total_stage=True
        )
        return result

