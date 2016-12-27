#!/usr/bin/env python

from __future__ import division, print_function

import argparse
import os
import re
import glob
import subprocess
import errno
import traceback
import time

from jinja2 import Environment, FileSystemLoader

import pandas as pd


os.chdir(os.path.dirname(os.path.abspath(__file__)))


class AnsiColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_warn(*args):
    print(AnsiColors.WARN, end="")
    print(*args)
    print(AnsiColors.ENDC, end="")


def print_bold(*args):
    print(AnsiColors.BOLD, end="")
    print(*args)
    print(AnsiColors.ENDC, end="")


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


def plot_path(benchmark_name):
    return os.path.join(
        "plots",
        "{:02d}_{}".format(benchmark_id[benchmark_name], benchmark_name),
    )


def plot_csv_path(benchmark_name, stage_id, stage):
    return os.path.join(
        "plots",
        "{:02d}_{}".format(benchmark_id[benchmark_name], benchmark_name),
        "{:02d}_{}_plot.csv".format(stage_id, stage)
    )


class Wordcount(object):

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
                from data.generate_text import generate
                generate(f, Wordcount.sizes[size])

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
                        print(traceback.format_stack())

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


benchmark_meta = {
    "wordcount": Wordcount
}

benchmark_id = {
    "wordcount": 1,
}


class Benchmark(object):
    """
    Better names?
        BenchmarkEntry
        BenchmarkLocator
        BenchmarkEntryLocator
        ImplementationLocator
        ResultLocator
    """

    def __init__(self, language, benchmark_id, benchmark_name, impl_id, impl_name):
        self.language = language
        self.benchmark_id = int(benchmark_id)
        self.benchmark_name = benchmark_name
        self.impl_id = int(impl_id)
        self.impl_name = impl_name

    @property
    def impl_path(self):
        return os.path.join(
            "benchmarks",
            self.language,
            "{:02d}_{}".format(self.benchmark_id, self.benchmark_name),
            "{:02d}_{}".format(self.impl_id, self.impl_name)
        )

    @property
    def result_path(self):
        return os.path.join(
            "results",
            # "stdout",
            self.language,
            "{:02d}_{}".format(self.benchmark_id, self.benchmark_name),
            "{:02d}_{}".format(self.impl_id, self.impl_name)
        )

    def result_files(self, size):
        pattern = os.path.join(self.result_path, "stdout_run_{}_*".format(size))
        return sorted(glob.glob(pattern))

    @property
    def label(self):
        s = self.language
        if self.impl_id > 1:
            s += " / " + self.impl_name
        return s

    def build(self):

        build_script_path = os.path.join(
            self.impl_path, "build.sh"
        )
        if not os.path.exists(build_script_path):
            return

        print(" *** Building: {} / {} / {}".format(
            self.language, self.benchmark_name, self.impl_name
        ))
        p = subprocess.Popen(
            [
                "/bin/bash",
                "build.sh"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.impl_path
        )
        stdout, stderr = p.communicate()
        if len(stderr) > 0:
            raise RuntimeError(stderr)

    def run(self, args, stdout_filename):
        # print(" *** Running: {} / {} / {}".format(
        #    self.language, self.benchmark_name, self.impl_name
        #))
        p = subprocess.Popen(
            [
                "/bin/bash",
                "run.sh"
            ] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.impl_path
        )
        stdout, stderr = p.communicate()
        if len(stderr) > 0:
            raise RuntimeError(stderr)

        # TODO handle return codes

        print("Read stdout of length: {}".format(len(stdout)))
        print(stdout)

        out_path = stdout_filename
        ensure_dir_exists(out_path)
        f = open(out_path, "w")
        f.write(stdout)

    def __repr__(self):
        return "BenchmarkEntry({}, {}, {})".format(
            self.language,
            self.benchmark_name,
            self.impl_name
        )


def ensure_dir_exists(path):
    dir_path = os.path.dirname(path)
    try:
        os.makedirs(dir_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir_path):
            pass
        else:
            raise


def discover_benchmark_entries(prefix):
    entries = []

    entry_paths = sorted(
        glob.glob(prefix + '/*/*/*'),
        key=lambda s: s.lower()
    )

    for path in entry_paths:
        m = re.match(prefix + "/(.*)/(\d+)_(.*)/(\d+)_(.*)", path)
        if m is not None:
            language = m.group(1)
            benchmark_id = m.group(2)
            benchmark_name = m.group(3)
            impl_id = m.group(4)
            impl_name = m.group(5)
            # print(language, benchmark_name, impl_name)
            entries += [
                Benchmark(language, benchmark_id, benchmark_name, impl_id, impl_name)
            ]

    return entries


"""
def run_benchmark(benchmark):
    print_bold("\nBenchmarking: {} / {} / {}".format(
        benchmark.language, benchmark.benchmark_name, benchmark.impl_name
    ))

    # check data
    meta_data = benchmark_meta[benchmark.benchmark_name]
    meta_data.ensure_data_exists()

    # build
    benchmark.build()

    # run
    args = meta_data.benchmark_args
    for iter in xrange(9):
        benchmark.run(args, run_id=iter+1)
"""


def run_all_benchmarks(benchmark_entries):

    # data generation
    benchmark_names = set([b_entry.benchmark_name for b_entry in benchmark_entries])
    for benchmark_name in benchmark_names:
        print_bold("\nPreparing Benchmark: {}".format(
            benchmark_name
        ))

        # check data
        b_meta_data = benchmark_meta[b_entry.benchmark_name]

        t1 = time.time()
        b_meta_data.ensure_data_exists()
        t2 = time.time()
        print("[{:6.1f} sec]".format(t2 - t1))

    # build
    for b_entry in benchmark_entries:
        print_bold("\nBuilding: {} / {} / {}".format(
            b_entry.language, b_entry.benchmark_name, b_entry.impl_name,
        ))

        # build
        t1 = time.time()
        b_entry.build()
        t2 = time.time()
        print("[{:6.1f} sec]".format(t2 - t1))

    # run
    # TODO: apply randomized order to minimize load effects
    runs = [
        (b, size, run_id)
        for b in benchmark_entries
        for size in [Sizes.S, Sizes.M, Sizes.L]
        for run_id in [1, 2, 3]
    ]

    for i, (b_entry, size, run_id) in enumerate(runs):
        # run_benchmark(benchmark)

        print_bold("\nRunning benchmark [{} / {}]: {} / {} / {} / {} / {}".format(
            i + 1, len(runs),
            b_entry.language, b_entry.benchmark_name, b_entry.impl_name,
            size, run_id,
        ))

        # run
        args = b_meta_data.benchmark_args(size)
        stdout_filename = os.path.join(b_entry.result_path, "stdout_run_{}_{:04d}".format(size, run_id))

        t1 = time.time()
        b_entry.run(args, stdout_filename)
        t2 = time.time()
        print("[{:6.1f} sec]".format(t2 - t1))


def visualize_benchmark_html(name, benchmark_entries, meta_data):
    print_bold("\nVisualizing: " + name)

    num_entries = len(benchmark_entries)

    # The extractors return a dict of "stage => list of runtimes", i.e,
    # run_times_per_stage becomes a "dict[benchmark_entry][stage] => list of runtimes"
    run_times_per_stage = {
        b_entry: meta_data.result_extractor(b_entry) for b_entry in benchmark_entries
    }

    stage_id = 0
    for stage in meta_data.stages:
        stage_id += 1

        rows = []
        for b_entry in benchmark_entries:
            run_times = run_times_per_stage[b_entry][stage]
            row = {
                "lang": b_entry.language,
                "descr": "",
            }
            for i, value in enumerate(run_times):
                row["run_{}".format(i+1)] = value
            rows.append(row)

        plot_csv = plot_csv_path(name, stage_id, stage)
        ensure_dir_exists(plot_csv)

        schema = ["lang", "descr"] + ["run_{}".format(i+1) for i in xrange(9)]
        with open(plot_csv, "w") as f:
            f.write(";".join(schema) + "\n")
            for row in rows:
                out_row = ";".join([str(row[field]) for field in schema])
                f.write(out_row + "\n")

    # prepare template code
    plot_calls = []
    divs = []
    stage_id = 0
    for stage in meta_data.stages:
        stage_id += 1

        plot_csv_basename = os.path.basename(plot_csv_path(name, stage_id, stage))
        plot_calls += [
            'visualizeCsv("{}", "#plot{}");'.format(
                plot_csv_basename,
                stage_id
            )
        ]
        divs += [
            '<div id="plot{}"></div>'.format(stage_id)
        ]

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('plot.html')
    html = template.render(
        plot_calls=plot_calls,
        divs=divs,
    )

    out_path = os.path.join(plot_path(name), "plot.html")
    with open(out_path, "w") as f:
        f.write(html)


def visualize_all_benchmarks():
    benchmarks = discover_benchmark_entries("benchmarks")


def read_file(filename):
    with open(filename) as f:
        text = f.read()
    return text


def write_file(filename, text):
    with open(filename, 'w') as f:
        f.write(text)


def generate_markdown():

    readme_text = read_file("templates/README.template.md")
    write_file("README.md", readme_text)

    benchmark_templates = [
        "templates/01_wordcount.template.md"
    ]
    for benchmark_template in benchmark_templates:
        text = read_file(benchmark_template)
        out_path = os.path.basename(benchmark_template.replace(".template", ""))
        write_file(out_path, text)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark runner framework",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--benchmark",
        nargs="+",
        help="Filter benchmarks to run by benchmark name(s).")
    parser.add_argument(
        "--lang",
        nargs="+",
        help="Filter benchmarks to run by programming language(s).")
    parser.add_argument(
        "-p", "--plot-only",
        action='store_true',
        help="Do not re-run benchmarks, only visualize.")
    parsed = parser.parse_args()
    return parsed


if __name__ == "__main__":

    args = parse_args()

    # TODO filter & determine affected benchmarks for visualization
    if not args.plot_only:
        benchmark_entries = discover_benchmark_entries("benchmarks")  # TODO: rename to implementations
        run_all_benchmarks(benchmark_entries)

    all_benchmarks_results = discover_benchmark_entries("results")

    for benchmark_name in ["wordcount"]:
        results = [
            result for result in all_benchmarks_results if result.benchmark_name == benchmark_name
        ]
        meta_data = benchmark_meta[benchmark_name]
        visualize_benchmark_html(benchmark_name, results, meta_data)

    generate_markdown()

