#!/usr/bin/env python

from __future__ import division, print_function

import textwrap
import os
import traceback

from ..base import *
from ..utils import *
from .. import generators


class Wordcount(object):

    title = "Wordcount"

    description = textwrap.dedent("""\
    Perform a simple word count on a text file.
    To isolate I/O from other aspects, all solutions should implement the following stages:

    - **IO**: Read entire file into memory (one large string).
    - **Split**: Split string on split characters: `'\\n'` and `' '` (single space)
    - **Count**: Iterate over words to build a hash map with counts.

    Benchmark aspects: Hash maps, basic string operations, allocation

    <div class="page-header"></div>
    #### Input

    - Path of text file to read.

    <div class="page-header"></div>
    #### Control Output

    After writing the stage runtimes to STDOUT, the implementations should print:

    - Size of the word map
    - Sum of the counts in the map

    """)

    _datafile = {
        Sizes.S: os.path.abspath("data/generated/random_words_S.txt"),
        Sizes.M: os.path.abspath("data/generated/random_words_M.txt"),
        Sizes.L: os.path.abspath("data/generated/random_words_L.txt"),
    }

    sizes = {
        Sizes.S:   1 * 1000 * 1000,
        Sizes.M:  10 * 1000 * 1000,
        Sizes.L: 100 * 1000 * 1000,
    }

    stages = ["Total", "IO", "Split", "Count"]

    linear_scales = {
        "Total": True,
        "IO": True,
        "Split": True,
        "Count": True,
    }

    @staticmethod
    def benchmark_args(size):
        return [Wordcount._datafile[size]]

    @staticmethod
    def ensure_data_exists():
        for size, f in Wordcount._datafile.iteritems():
            if not os.path.exists(f):
                print_warn(
                    " *** Generating data [{}], this might take a while...".format(f)
                )
                generators.generate_text(f, Wordcount.sizes[size])

    @staticmethod
    def result_extractor(b_entry):
        # TODO: should we do the result validation here (when collecting the runtimes,
        # TODO: better name would probably be "extract_runtimes") or should there be
        # TODO: a separate "result_validator"? Probably the latter...
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
            "IO": runtimes_io,
            "Split": runtimes_split,
            "Count": runtimes_count,
        }
        return result
