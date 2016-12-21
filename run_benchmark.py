#!/usr/bin/env python

from __future__ import division, print_function

import os
import re
import glob
import subprocess
import errno
import traceback
import warnings

import matplotlib.pyplot as plt

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import seaborn
    seaborn.set()

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


def wordcount_extractor(files):
    runtimes_io = []
    runtimes_split = []
    runtimes_count = []
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

    N = len(files)
    result = {
        "IO": sum(runtimes_io) / N,
        "Split": sum(runtimes_split) / N,
        "Count": sum(runtimes_count) / N,
    }
    return result


benchmark_extractors = {
    "wordcount": wordcount_extractor,
}


class Wordcount(object):

    _datafile = os.path.abspath("data/generated/random_words.txt")

    stages = ["IO", "Split", "Count"]
    benchmark_args = [_datafile]

    @staticmethod
    def ensure_data_exists():
        if not os.path.exists(Wordcount._datafile):
            print_warn(
                " *** Generating data for 'word_count', this might take a while..."
            )
            from data.generate_text import generate
            generate(Wordcount._datafile)




benchmark_meta = {
    "wordcount": Wordcount
}

benchmark_id = {
    "wordcount": 1,
}


class Benchmark(object):

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

    @property
    def result_files(self):
        pattern = os.path.join(self.result_path, "stdout_run_*")
        return glob.glob(pattern)

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

    def run(self, args, run_id):
        print(" *** Running: {} / {} / {}".format(
            self.language, self.benchmark_name, self.impl_name
        ))
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

        out_path = os.path.join(self.result_path, "stdout_run_{:04d}".format(run_id))
        ensure_dir_exists(out_path)
        f = open(out_path, "w")
        f.write(stdout)


def ensure_dir_exists(path):
    dir_path = os.path.dirname(path)
    try:
        os.makedirs(dir_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir_path):
            pass
        else:
            raise


def discover_benchmarks(prefix):
    impls = []

    implementation_paths = glob.glob(prefix + '/*/*/*')

    for impl_path in implementation_paths:
        m = re.match(prefix + "/(.*)/(\d+)_(.*)/(\d+)_(.*)", impl_path)
        if m is not None:
            language = m.group(1)
            benchmark_id = m.group(2)
            benchmark_name = m.group(3)
            impl_id = m.group(4)
            impl_name = m.group(5)
            # print(language, benchmark_name, impl_name)
            impls += [
                Benchmark(language, benchmark_id, benchmark_name, impl_id, impl_name)
            ]

    return impls


def run_benchmark(benchmark):
    print_bold("\nBenchmarking: " + benchmark.benchmark_name)

    # check data
    meta_data = benchmark_meta[benchmark.benchmark_name]
    meta_data.ensure_data_exists()

    # build
    benchmark.build()

    # run
    args = meta_data.benchmark_args
    for iter in xrange(3):
        benchmark.run(args, run_id=iter+1)


def run_all_benchmarks():
    benchmarks = discover_benchmarks("benchmarks")
    for benchmark in benchmarks:
        run_benchmark(benchmark)


run_all_benchmarks()


def visualize_benchmark(name, results):
    print_bold("\nVisualizing: " + name)

    filtered = [
        result for result in results if result.benchmark_name == name
    ]
    extractor = benchmark_extractors[name]
    run_times = {
        result: extractor(result.result_files) for result in filtered
    }
    meta_data = benchmark_meta[name]

    stage_id = 0
    for stage in meta_data.stages:
        stage_id += 1

        num_entries = len(filtered)
        y_size = (num_entries + 2) * 0.4    # = 40 pixel per row

        fig, ax = plt.subplots(1, 1, figsize=(10, y_size))
        plt.subplots_adjust(
            bottom=1 / (num_entries+2),
            top=1 - 1 / (num_entries+2)
        )

        xs = []
        labels = []
        for result in filtered:
            rt = run_times[result][stage]
            xs.append(rt)
            labels.append(result.label)
            # print(rt)

        ys = range(len(xs))
        ax.plot(xs, ys, 'o')

        ax.set_yticks(ys)
        ax.set_yticklabels(labels)
        ax.set_ylim(-0.5, len(labels) - 0.5)
        ax.yaxis.tick_right()

        plot_file_name = os.path.join(
            "plots",
            "{:02d}_{}".format(benchmark_id[name], name),
            "{:02d}_{}_runtimes.png".format(stage_id, stage)
        )
        ensure_dir_exists(plot_file_name)
        plt.savefig(plot_file_name)
    #import IPython; IPython.embed()


benchmarks_results = discover_benchmarks("results")
visualize_benchmark("wordcount", benchmarks_results)


def visualize_all_benchmarks():
    benchmarks = discover_benchmarks("benchmarks")


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

generate_markdown()