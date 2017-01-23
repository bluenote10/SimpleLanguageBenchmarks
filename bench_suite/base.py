#!/usr/bin/env python

from __future__ import division, print_function

import traceback
from .utils import print_error


class Sizes(object):
    S = "S"
    M = "M"
    L = "L"

    class __metaclass__(type):
        def __iter__(self):
            return iter([
                Sizes.S,
                Sizes.M,
                Sizes.L,
            ])

        def __len__(self):
            return 3


def default_runtime_extractor(b_entry, stage_names, add_total_stage=True):

    num_stages = len(stage_names)
    runtimes_per_stage = [[] for _ in stage_names]

    for size in Sizes:
        files = b_entry.result_files(size)
        for fn in files:
            with open(fn) as f:
                try:
                    for i in xrange(num_stages):
                        t = float(f.readline())
                        runtimes_per_stage[i].append(t)
                except ValueError, e:
                    print_error("Output did not fulfil expected format:")
                    print(traceback.format_exc())

    result = {
        stage: runtimes_per_stage[j] for j, stage in enumerate(stage_names)
    }

    if add_total_stage:
        N = len(runtimes_per_stage[0])
        runtimes_total = [
            sum([runtimes_per_stage[j][i] for j in xrange(num_stages)])
            for i in xrange(N)
        ]
        result["Total"] = runtimes_total

    return result

