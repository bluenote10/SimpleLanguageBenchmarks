#!/usr/bin/env python

from __future__ import division, print_function

import textwrap
import os

from ..base import Sizes, default_runtime_extractor
from ..utils import print_warn
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

    After writing the stage run times to STDOUT, the implementations should print:

    - Size of the word map
    - Sum of the counts in the map

    """)

    _datafile = {
        Sizes.S: os.path.abspath("data/generated/random_words_S.txt"),
        Sizes.M: os.path.abspath("data/generated/random_words_M.txt"),
        Sizes.L: os.path.abspath("data/generated/random_words_L.txt"),
    }

    sizes = {
        Sizes.S:   1 * 1024 * 1024,
        Sizes.M:  10 * 1024 * 1024,
        Sizes.L: 100 * 1024 * 1024,
    }

    @classmethod
    def size_description(cls, size):
        return "file size = ~{} MB".format(cls.sizes[size] / 1024 / 1024)

    stages = ["Total", "IO", "Split", "Count"]

    linear_scales = {
        "Total": True,
        "IO": True,
        "Split": True,
        "Count": True,
    }

    @classmethod
    def benchmark_args(cls, size):
        return [cls._datafile[size]]

    @classmethod
    def ensure_data_exists(cls):
        for size, f in cls._datafile.iteritems():
            if not os.path.exists(f):
                print_warn(
                    " *** Generating data [{}], this might take a while...".format(f)
                )
                generators.generate_text(f, cls.sizes[size])

    @classmethod
    def result_extractor(cls, b_entry):
        result = default_runtime_extractor(
            b_entry,
            cls.stages[1:],
            add_total_stage=True
        )
        return result

