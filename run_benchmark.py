#!/usr/bin/env python

from __future__ import print_function

import os
import re
import glob
import subprocess
import errno

import matplotlib.pyplot as plt
import seaborn
seaborn.set()


os.chdir(os.path.dirname(os.path.abspath(__file__)))


def wordcount_extractor(files):
    runtimes_io = []
    runtimes_split = []
    runtimes_count = []
    for fn in files:
        with open(fn) as f:
            t1 = float(f.readline())
            t2 = float(f.readline())
            t3 = float(f.readline())
            runtimes_io.append(t1)
            runtimes_split.append(t2)
            runtimes_count.append(t3)

    N = len(files)
    result = {
        "IO": sum(runtimes_io) / N,
        "Split": sum(runtimes_split) / N,
        "Count": sum(runtimes_count) / N,
    }
    return result


benchmark_args = {
    "wordcount": [
        os.path.abspath("data/generated/random_words.txt.gz")
    ]
}

benchmark_extractors = {
    "wordcount": wordcount_extractor,
}


class Wordcount(object):

    stages = ["IO", "Split", "Count"]


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
        pass

    def run(self, args, run_id):
        # runner = os.path.join(self.path, "run.sh")
        #"["run.sh"] + args
        """
        p = subprocess.Popen(
            "run.sh",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=self.path
        )
        """
        p = subprocess.Popen(
            [
                "/bin/bash",
                "run.sh"
            ] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.path
        )
        stdout, stderr = p.communicate()
        if len(stderr) > 0:
            raise RuntimeError(stderr)

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
            print(language, benchmark_name, impl_name)
            impls += [
                Benchmark(language, benchmark_id, benchmark_name, impl_id, impl_name)
            ]

    return impls


def run_benchmark(benchmark):
    benchmark.build()
    args = benchmark_args[benchmark.benchmark_name]
    benchmark.run(args, 1)


def run_all_benchmarks():
    benchmarks = discover_benchmarks("benchmarks")
    for benchmark in benchmarks:
        run_benchmark(benchmark)


def visualize_benchmark(name, results):
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

        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        xs = []
        labels = []
        for result in filtered:
            rt = run_times[result][stage]
            xs.append(rt)
            labels.append(result.label)
            print(rt)
        ys = range(len(xs))
        ax.plot(xs, ys, 'o')

        ax.set_yticks(ys)
        ax.set_yticklabels(labels)
        ax.set_ylim(-0.5, len(labels) - 0.5)

        plot_file_name = os.path.join(
            "plots",
            "{}_{}".format(benchmark_id[name], name),
            "{:02d}_{}_runtimes.png".format(stage_id, stage)
        )
        ensure_dir_exists(plot_file_name)
        plt.savefig(plot_file_name)
    import IPython; IPython.embed()

benchmarks_results = discover_benchmarks("results")
visualize_benchmark("wordcount", benchmarks_results)

def visualize_all_benchmarks():
    benchmarks = discover_benchmarks("benchmarks")

