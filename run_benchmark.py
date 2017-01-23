#!/usr/bin/env python

from __future__ import division, print_function

import argparse
import os

from bench_suite.core import *


os.chdir(os.path.dirname(os.path.abspath(__file__)))


# -----------------------------------------------------------------------------
# Argument parsing
# -----------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark runner framework",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--num-repetitions",
        type=int,
        default=5,
        help="Number of repetitions for each benchmark (default: 3).")
    parser.add_argument(
        "--benchmark",
        nargs="+",
        default=[],
        help="Filter benchmarks to run by benchmark name(s).")
    parser.add_argument(
        "--lang",
        nargs="+",
        default=[],
        help="Filter benchmarks to run by programming language(s).")
    parser.add_argument(
        "-p", "--plot-only",
        action='store_true',
        help="Do not re-run benchmarks, only visualize.")
    parser.add_argument(
        "-r", "--run-only",
        action='store_true',
        help="Do not run visualization, only run benchmarks.")
    parsed = parser.parse_args()
    return parsed


def main():

    args = parse_args()

    if not args.plot_only:
        all_benchmark_entries = discover_benchmark_entries("implementations")
        benchmark_entries = filter_benchmark_entries(
            all_benchmark_entries,
            args.lang,
            args.benchmark,
        )
        run_all_benchmarks(benchmark_entries, args.num_repetitions)

    if not args.run_only:
        all_benchmark_entries = discover_benchmark_entries("results")
        # Note for visualization we probably never want to filter

        affected_benchmarks = set([b_entry.benchmark_name for b_entry in all_benchmark_entries])

        for benchmark_name in affected_benchmarks:
            entries_of_benchmark = [
                b_entry for b_entry in all_benchmark_entries
                if b_entry.benchmark_name == benchmark_name
            ]
            meta_data = benchmark_meta[benchmark_name]
            generate_benchmark_html(benchmark_name, entries_of_benchmark, meta_data)

        generate_summary_html(affected_benchmarks, all_benchmark_entries)
        generate_summary_markdown()


if __name__ == "__main__":
    main()
