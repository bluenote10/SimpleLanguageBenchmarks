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
import textwrap
import platform
import random
import datetime

import data.generators as generators

import numpy as np
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader, StrictUndefined


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


def print_error(*args):
    print(AnsiColors.FAIL, end="")
    print(*args)
    print(AnsiColors.ENDC, end="")


def print_warn(*args):
    print(AnsiColors.WARN, end="")
    print(*args)
    print(AnsiColors.ENDC, end="")


def print_bold(*args):
    print(AnsiColors.BOLD, end="")
    print(*args)
    print(AnsiColors.ENDC, end="")


def read_file(filename):
    with open(filename) as f:
        text = f.read()
    return text


def write_file(filename, text):
    with open(filename, 'w') as f:
        f.write(text)


def ensure_dir_exists(path):
    dir_path = os.path.dirname(path)
    try:
        os.makedirs(dir_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir_path):
            pass
        else:
            raise


def write_csv_with_schema(filename, rows, schema):
    ensure_dir_exists(filename)
    with open(filename, "w") as f:
        f.write(";".join(schema) + "\n")
        for row in rows:
            out_row = ";".join([str(row[field]) for field in schema])
            f.write(out_row + "\n")


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


def html_path():
    return "docs"


def html_path_benchmark(benchmark_name):
    return os.path.join(
        html_path(),
        "{:02d}_{}".format(benchmark_id[benchmark_name], benchmark_name),
    )


def html_path_raw_runtime_csv(benchmark_name, stage_id, stage):
    return os.path.join(
        html_path_benchmark(benchmark_name),
        "{:02d}_{}_plot.csv".format(stage_id, stage),
    )


def html_path_stage_summary_csv(benchmark_name, stage_id, stage):
    return os.path.join(
        html_path_benchmark(benchmark_name),
        "stage_summary.csv",
    )


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


benchmark_meta = {
    "Wordcount": Wordcount,
    "BasicMatOps": BasicMatOps,
    "Fibonacci": Fibonacci,
}

benchmark_id = {
    "Wordcount": 1,
    "BasicMatOps": 2,
    "Fibonacci": 3,
}


class BenchmarkEntry(object):

    def __init__(self, language, benchmark_id, benchmark_name, impl_id, impl_name):
        self.language = language
        self.benchmark_id = int(benchmark_id)
        self.benchmark_name = benchmark_name
        self.impl_id = int(impl_id)
        self.impl_name = impl_name

    @property
    def impl_path(self):
        return os.path.join(
            "implementations",
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
    def impl_suffix(self):
        fields = self.impl_name.split("_")
        return ", ".join(fields)

    def build(self):

        build_script_path = os.path.join(
            self.impl_path, "build.sh"
        )
        if not os.path.exists(build_script_path):
            return

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
            print_warn(
                "Build has written to STDERR (which may or may not be an issue):"
            )
            print(stderr)

        # TODO: add switch for making build failures fatal
        print("Return code: {}".format(p.returncode))
        if p.returncode != 0:
            print_error(
                "Build has failed."
            )
            print("STDOUT:\n" + stdout)
            print("STDERR:\n" + stderr)
            import sys; sys.exit(1)

    def run(self, args, stdout_filename):
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

        print("Return code: {}".format(p.returncode))
        if p.returncode != 0:
            print_error(
                "Run has failed."
            )
            print("STDOUT:\n" + stdout)
            print("STDERR:\n" + stderr)

        else:
            print("Read stdout of length: {}".format(len(stdout)))
            print(stdout)

        out_path = stdout_filename
        ensure_dir_exists(out_path)
        f = open(out_path, "w")
        f.write(stdout)

    def get_meta_data(self):
        path = os.path.join(self.impl_path, "benchmark.yml")
        try:
            with open(path) as f:
                text = f.read()
        except IOError as exc:
            print_error("[ERROR] Failed to read meta data from '{}':".format(path))
            print(exc)
            text = None
        meta_data = None
        if text is not None:
            try:
                meta_data = yaml.load(text)
            except yaml.YAMLError as exc:
                print_error("[ERROR] Failed to parse YAML:")
                print(exc)
        return meta_data

    def __repr__(self):
        return "BenchmarkEntry({}, {}, {})".format(
            self.language,
            self.benchmark_name,
            self.impl_name
        )


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
                BenchmarkEntry(language, benchmark_id, benchmark_name, impl_id, impl_name)
            ]

    # make sure entries are sorted by benchmark, language, implemention
    entries.sort(key=lambda x:
        (x.benchmark_id, x.language, x.impl_id, x.impl_path)
    )

    return entries


def filter_benchmark_entries(entries, langs, benchmarks):
    filtered = []
    for entry in entries:
        lang_cond = len(langs) == 0 or entry.language in langs
        benchmark_cond = len(benchmarks) == 0 or entry.benchmark_name in benchmarks
        if lang_cond and benchmark_cond:
            filtered.append(entry)
    return filtered


# -----------------------------------------------------------------------------
# Benchmark running
# -----------------------------------------------------------------------------

def run_all_benchmarks(benchmark_entries, num_repetitions):

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
    runs = [
        (b, size, run_id)
        for b in benchmark_entries
        for size in [Sizes.S, Sizes.M, Sizes.L]
        for run_id in xrange(1, num_repetitions+1)
    ]
    # Maybe we want to shuffle only w.r.t language/run_id and keep sizes in order?
    random.shuffle(runs)

    for i, (b_entry, size, run_id) in enumerate(runs):

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


# -----------------------------------------------------------------------------
# Visualization
# -----------------------------------------------------------------------------

def locate_sub_pages(relative_path="."):
    sub_pages_folder = sorted(glob.glob(
        html_path() + "/*/index.html"
    ))
    sub_pages = []
    for sub_page in sub_pages_folder:
        folder_name = sub_page.split(os.path.sep)[-2]
        idx, name = folder_name.split("_")
        human_name = benchmark_meta[name].title
        relative_url = '/'.join(sub_page.split(os.path.sep)[-2:])
        relative_url = relative_path + "/" + relative_url
        sub_pages.append((human_name, relative_url))
    return sub_pages


def get_median_runtime_of_largest_size(run_times):
    filtered_run_times = []
    num_repetitions = len(run_times) // len(Sizes)
    for i, value in enumerate(run_times):
        size = {
            0: Sizes.S,
            1: Sizes.M,
            2: Sizes.L,
        }[i // num_repetitions]
        # filter on largest results
        if size == Sizes.L:
            filtered_run_times.append(value)

    return np.median(filtered_run_times)


def write_raw_runtime_csv(benchmark_name, run_times_per_stage, benchmark_entries, meta_data):

    for stage_id, stage in enumerate(meta_data.stages, 1):

        rows = []
        for b_entry in benchmark_entries:
            run_times = run_times_per_stage[b_entry][stage]
            num_repetitions = len(run_times) // len(Sizes)
            for i, value in enumerate(run_times):
                size = {
                    0: Sizes.S,
                    1: Sizes.M,
                    2: Sizes.L,
                }[i // num_repetitions]
                run_id = (i % num_repetitions) + 1
                row = {
                    "lang": b_entry.language,
                    "descr": b_entry.impl_suffix,
                    "label": b_entry.language + " (" + b_entry.impl_suffix + ")",
                    "size": size,
                    "run_id": run_id,
                    "time": value
                }
                rows.append(row)

        plot_csv = html_path_raw_runtime_csv(benchmark_name, stage_id, stage)

        write_csv_with_schema(
            plot_csv, rows,
            schema=["lang", "descr", "label", "size", "run_id", "time"]
        )


def write_stage_summary_csv(benchmark_name, run_times_per_stage, benchmark_entries, meta_data):

    rows = []

    for b_entry in benchmark_entries:

        for stage_id, stage in enumerate(meta_data.stages, 1):

            # ugly hack: don't add the total stage to these plots
            if stage == "Total":
                continue

            run_times = run_times_per_stage[b_entry][stage]
            median_of_largest_size = get_median_runtime_of_largest_size(run_times)

            row = {
                "lang": b_entry.language,
                "descr": b_entry.impl_suffix,
                "label": b_entry.language + " (" + b_entry.impl_suffix + ")",
                "stage": stage,
                "time": median_of_largest_size
            }
            rows.append(row)

    plot_csv = html_path_stage_summary_csv(benchmark_name, stage_id, stage)

    write_csv_with_schema(
        plot_csv, rows,
        schema=["lang", "descr", "label", "stage", "time"]
    )


def generate_benchmark_html(name, benchmark_entries, meta_data):
    num_entries = len(benchmark_entries)
    print_bold("\nRendering html of benchmark '{}' with {} entries".format(
        name, num_entries
    ))

    # The extractors return a dict of "stage => list of runtimes", i.e,
    # run_times_per_stage becomes a "dict[benchmark_entry][stage] => list of runtimes"
    run_times_per_stage = {
        b_entry: meta_data.result_extractor(b_entry) for b_entry in benchmark_entries
    }

    # extract and write CSVs
    write_raw_runtime_csv(name, run_times_per_stage, benchmark_entries, meta_data)
    write_stage_summary_csv(name, run_times_per_stage, benchmark_entries, meta_data)

    # prepare template code
    plot_calls = []
    plot_htmls = []
    stage_id = 0
    for stage in meta_data.stages:
        stage_id += 1

        linear_scale = meta_data.linear_scales[stage]

        plot_csv_basename = os.path.basename(html_path_raw_runtime_csv(name, stage_id, stage))
        plot_calls += [
            'visualizeCsv("{}", "#plot{}", {});'.format(
                plot_csv_basename,
                stage_id,
                "true" if linear_scale else "false"
            )
        ]
        div = '<div id="plot{}"></div>'.format(stage_id)
        plot_htmls += [
            (stage, div)
        ]

    # get implementation paths
    impl_locs = []
    for b_entry in benchmark_entries:
        entry_meta_data = b_entry.get_meta_data()
        if entry_meta_data is not None and "source-file" in entry_meta_data:
            url = b_entry.impl_path + "/" + entry_meta_data["source-file"]
            descr = entry_meta_data.get("description") or ""
            impl_locs += [(b_entry.language, url, descr)]
        else:
            impl_locs += [(b_entry.language, None, "")]

    # compile html
    html_description = markdown.markdown(meta_data.description)

    env = Environment(
        loader=FileSystemLoader('templates'),
        undefined=StrictUndefined,
    )
    benchmark_template = env.get_template('benchmark.html')

    # Navbar requires knowledge of all pages as well.
    sub_pages = locate_sub_pages("..")

    common_header = env.get_template('common_header.html').render(
        base_url="..",
    )
    navbar = env.get_template('navbar.html').render(
        sub_pages=sub_pages,
        url_home="../index.html",
    )

    html = benchmark_template.render(
        common_header=common_header,
        navbar=navbar,
        title=meta_data.title,
        description=html_description,
        impl_locs=impl_locs,
        plot_calls=plot_calls,
        plot_htmls=plot_htmls,
    )

    out_path = os.path.join(html_path_benchmark(name), "index.html")
    with open(out_path, "w") as f:
        f.write(html)


def write_general_summary_csv(affected_benchmarks, all_benchmark_entries):

    max_runtimes = dict()
    for benchmark_name in affected_benchmarks:
        benchmark_entries = [
            b_entry for b_entry in all_benchmark_entries
            if b_entry.benchmark_name == benchmark_name
            ]
        meta_data = benchmark_meta[benchmark_name]

        def get_max_runtime(b_entry):
            per_stage_result = meta_data.result_extractor(b_entry)
            return get_median_runtime_of_largest_size(per_stage_result["Total"])

        for b_entry in benchmark_entries:
            max_runtimes[b_entry] = get_max_runtime(b_entry)

    rows = []
    for b_entry in all_benchmark_entries:
        rows += [{
            "benchmark": b_entry.benchmark_name,
            "lang": b_entry.language,
            "descr": b_entry.impl_suffix,
            "label": b_entry.language + " (" + b_entry.impl_suffix + ")",
            "time": max_runtimes[b_entry]
        }]

    csv_filename = os.path.join(html_path(), "summary.csv")
    write_csv_with_schema(
        csv_filename, rows,
        schema=["benchmark", "lang", "descr", "label", "time"]
    )


def generate_summary_html(affected_benchmarks, all_benchmark_entries):
    print_bold("\nRendering main html")

    write_general_summary_csv(affected_benchmarks, all_benchmark_entries)

    sub_pages = locate_sub_pages(".")

    # load markdown elements and convert to html
    markdown_fragments = load_markdown_fragments(convert_to_html=True)

    env = Environment(
        loader=FileSystemLoader('templates'),
        undefined=StrictUndefined,
    )
    benchmark_template = env.get_template('main.html')

    common_header = env.get_template('common_header.html').render(
        base_url=".",
    )
    navbar = env.get_template('navbar.html').render(
        sub_pages=sub_pages,
        url_home="index.html",
    )

    html = benchmark_template.render(
        common_header=common_header,
        navbar=navbar,
        last_update=datetime.datetime.now().date().isoformat(),
        sub_pages=sub_pages,
        sys_specs=get_system_specs(),
        soft_specs=get_software_specs(),
        **markdown_fragments
    )

    out_path = os.path.join(html_path(), "index.html")
    with open(out_path, "w") as f:
        f.write(html)


def load_markdown_fragments(convert_to_html=False):
    fragments = [
        "contribute",
        "intro",
        "disclaimer",
        "framework",
        "license",
        "philosophy",
        "run_benchmarks",
    ]
    results = dict()
    for fragment in fragments:
        text = read_file("templates/_{}.md".format(fragment))
        if convert_to_html:
            text = markdown.markdown(text)
        results[fragment] = text
    return results


def generate_summary_markdown():

    env = Environment(
        loader=FileSystemLoader('templates'),
        undefined=StrictUndefined,
    )
    readme_template = env.get_template('README.md')

    markdown_fragments = load_markdown_fragments()

    readme_text = readme_template.render(
        **markdown_fragments
    )
    write_file("README.md", readme_text)


# -----------------------------------------------------------------------------
# Specs extraction
# -----------------------------------------------------------------------------

def match_line_in_text(text, pattern):
    for line in text.split("\n"):
        m = re.match(pattern, line)
        if m is not None:
            return m.group(1)
    return None


def match_line_from_file(filename, pattern):
    text = open(filename).read()
    return match_line_in_text(text, pattern)


def match_line_from_command(command, pattern):
    p = subprocess.Popen(
        [command],
        stdout=subprocess.PIPE,
    )
    stdout, stderr = p.communicate()
    return match_line_in_text(stdout, pattern)


def secure_execution(func, label):
    try:
        result = func()
        if result is not None:
            return result
        else:
            return "failed to determine"
    except Exception as exc:
        print_warn("Failed to get information for '{}':".format(label))
        print(exc)
        return "failed to determine"


def get_system_specs():

    def get_mem():
        mem_total_kB = float(match_line_from_file('/proc/meminfo', 'MemTotal:\s+(\d+)'))
        if mem_total_kB is not None:
            return "{:.1f} MB".format(mem_total_kB / 1024)

    def get_distribution():
        return match_line_from_file("/etc/lsb-release", 'DISTRIB_DESCRIPTION="(.*)"')

    def get_cpu_model():
        return match_line_from_file("/proc/cpuinfo", 'model name\s+:\s+(.*)')

    def get_cpu_cores():
        return match_line_from_file("/proc/cpuinfo", 'cpu cores\s+:\s+(.*)')

    def get_cpu_cache_size_l1d():
        return match_line_from_command("lscpu", 'L1d cache:\s+(.*)')

    def get_cpu_cache_size_l1i():
        return match_line_from_command("lscpu", 'L1i cache:\s+(.*)')

    def get_cpu_cache_size_l2():
        return match_line_from_command("lscpu", 'L2 cache:\s+(.*)')

    def get_cpu_cache_size_l3():
        return match_line_from_command("lscpu", 'L3 cache:\s+(.*)')

    spec_getters = [
        ("OS", platform.system),
        ("Distribution", get_distribution),
        ("Kernel", platform.release),
        ("CPU", get_cpu_model),
        ("Number of cores", get_cpu_cores),
        ("L1 data cache size", get_cpu_cache_size_l1d),
        ("L1 instruction cache size", get_cpu_cache_size_l1i),
        ("L2 cache size", get_cpu_cache_size_l2),
        ("L3 cache size", get_cpu_cache_size_l3),
        ("Memory", get_mem)
    ]

    specs = [
        (label, secure_execution(func, label))
        for label, func in spec_getters
    ]
    return specs


def get_line_from_command(command, lineno=0):
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = p.communicate()
    # some programs write version info to stderr
    if stdout == '':
        stdout = stderr
    lines = stdout.split("\n")
    return lines[lineno]


def get_software_specs():
    spec_getters = [
        ("GCC", lambda: get_line_from_command("gcc --version")),
        ("Clang", lambda: get_line_from_command("clang++-3.8 --version")),
        ("JVM", lambda: get_line_from_command("java -version", 1)),
        ("Python", lambda: get_line_from_command("python --version")),
        ("Nim", lambda: get_line_from_command("nim --version")),
    ]

    specs = [
        (label, secure_execution(func, label))
        for label, func in spec_getters
    ]
    return specs


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
        default=3,
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
