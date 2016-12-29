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
import yaml
import platform
import random

import markdown
from jinja2 import Environment, FileSystemLoader, StrictUndefined

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


def html_path():
    return "html"


def html_path_benchmark(benchmark_name):
    return os.path.join(
        html_path(),
        "{:02d}_{}".format(benchmark_id[benchmark_name], benchmark_name),
    )


def html_path_stage_csv(benchmark_name, stage_id, stage):
    return os.path.join(
        html_path_benchmark(benchmark_name),
        "{:02d}_{}_plot.csv".format(stage_id, stage),
    )


class Wordcount(object):

    title = "Wordcount"

    description = textwrap.dedent("""\
    ## Benchmark: Wordcount

    ### Task

    Perform a simple word count on a text file.
    To isolate I/O from other aspects, all solutions should implement the following stages:

    - **IO**: Read entire file into memory (one large string).
    - **Split**: Split string on split characters: `'\\n'` and `' '` (single space)
    - **Count**: Iterate over words to build a hash map with counts.

    Benchmark Aspects: Hash maps, basic string operations, allocation

    #### Input

    - Path of text file to read.

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
            raise RuntimeError(stderr)

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

        # TODO handle return codes

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
    runs = [
        (b, size, run_id)
        for b in benchmark_entries
        for size in [Sizes.S, Sizes.M, Sizes.L]
        for run_id in [1, 2, 3]
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

def visualize_benchmark_html(name, benchmark_entries, meta_data):
    num_entries = len(benchmark_entries)
    print_bold("\nRendering html of benchmark '{}' with {} entries".format(
        name, num_entries
    ))

    # The extractors return a dict of "stage => list of runtimes", i.e,
    # run_times_per_stage becomes a "dict[benchmark_entry][stage] => list of runtimes"
    run_times_per_stage = {
        b_entry: meta_data.result_extractor(b_entry) for b_entry in benchmark_entries
    }

    stage_id = 0
    for stage in meta_data.stages:
        stage_id += 1

        """
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

        plot_csv = html_path_stage_csv(name, stage_id, stage)
        ensure_dir_exists(plot_csv)

        schema = ["lang", "descr"] + ["run_{}".format(i+1) for i in xrange(9)]
        with open(plot_csv, "w") as f:
            f.write(";".join(schema) + "\n")
            for row in rows:
                out_row = ";".join([str(row[field]) for field in schema])
                f.write(out_row + "\n")
        """
        rows = []
        for b_entry in benchmark_entries:
            run_times = run_times_per_stage[b_entry][stage]
            for i, value in enumerate(run_times):
                # TODO: make configurable
                size = {
                    0: Sizes.S,
                    1: Sizes.M,
                    2: Sizes.L,
                }[i // 3]
                run_id = i % 3
                row = {
                    "lang": b_entry.language,
                    "descr": b_entry.impl_suffix,
                    "label": b_entry.language + " (" + b_entry.impl_suffix + ")",
                    "size": size,
                    "run_id": run_id,
                    "time": value
                }
                rows.append(row)

        plot_csv = html_path_stage_csv(name, stage_id, stage)
        ensure_dir_exists(plot_csv)

        schema = ["lang", "descr", "label", "size", "run_id", "time"]
        with open(plot_csv, "w") as f:
            f.write(";".join(schema) + "\n")
            for row in rows:
                out_row = ";".join([str(row[field]) for field in schema])
                f.write(out_row + "\n")

    # prepare template code
    plot_calls = []
    plot_htmls = []
    stage_id = 0
    for stage in meta_data.stages:
        stage_id += 1

        plot_csv_basename = os.path.basename(html_path_stage_csv(name, stage_id, stage))
        plot_calls += [
            'visualizeCsv("{}", "#plot{}");'.format(
                plot_csv_basename,
                stage_id
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
            url = "../../" + b_entry.impl_path + "/" + entry_meta_data["source-file"]
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

    common_header = env.get_template('common_header.html').render(
        base_url="..",
    )
    navbar = env.get_template('navbar.html').render(
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


def visualize_summary_html():
    print_bold("\nRendering main html")

    sub_pages_folder = sorted(glob.glob(
        html_path() + "/*/index.html"
    ))
    sub_pages = []
    for sub_page in sub_pages_folder:
        folder_name = sub_page.split(os.path.sep)[-2]
        idx, name = folder_name.split("_")
        human_name = benchmark_meta[name].title
        relative_url = '/'.join(sub_page.split(os.path.sep)[-2:])
        sub_pages.append((human_name, relative_url))

    # compile html
    # html_description = markdown.markdown(meta_data.description)

    env = Environment(
        loader=FileSystemLoader('templates'),
        undefined=StrictUndefined,
    )
    benchmark_template = env.get_template('main.html')

    common_header = env.get_template('common_header.html').render(
        base_url=".",
    )
    navbar = env.get_template('navbar.html').render(
        url_home="index.html",
    )

    html = benchmark_template.render(
        common_header=common_header,
        navbar=navbar,
        sub_pages=sub_pages,
        sys_specs=get_sys_specs(),
        soft_specs=get_soft_specs(),
    )

    out_path = os.path.join(html_path(), "index.html")
    with open(out_path, "w") as f:
        f.write(html)


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


def get_sys_specs():

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


def get_soft_specs():
    spec_getters = [
        ("GCC", lambda: get_line_from_command("gcc --version")),
        ("Python", lambda: get_line_from_command("python --version")),
    ]

    specs = [
        (label, secure_execution(func, label))
        for label, func in spec_getters
    ]
    return specs

# -----------------------------------------------------------------------------
# Specs extraction
# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------
# Argument parsing
# -----------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark runner framework",
        formatter_class=argparse.RawTextHelpFormatter)
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


if __name__ == "__main__":

    args = parse_args()

    if not args.plot_only:
        all_benchmark_entries = discover_benchmark_entries("implementations")
        benchmark_entries = filter_benchmark_entries(
            all_benchmark_entries,
            args.lang,
            args.benchmark,
        )
        run_all_benchmarks(benchmark_entries)

    if not args.run_only:
        all_benchmark_entries = discover_benchmark_entries("results")
        benchmark_entries = filter_benchmark_entries(
            all_benchmark_entries,
            args.lang,
            args.benchmark,
        )

        affected_benchmarks = set([b_entry.benchmark_name for b_entry in benchmark_entries])

        for benchmark_name in affected_benchmarks:
            entries_of_benchmark = [
                b_entry for b_entry in benchmark_entries
                if b_entry.benchmark_name == benchmark_name
            ]
            meta_data = benchmark_meta[benchmark_name]
            visualize_benchmark_html(benchmark_name, entries_of_benchmark, meta_data)

        visualize_summary_html()
