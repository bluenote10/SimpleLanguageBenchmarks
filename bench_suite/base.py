#!/usr/bin/env python

from __future__ import division, print_function


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

