#!/usr/bin/env python

from __future__ import print_function

import os
import re
import glob
import subprocess
import errno


os.chdir(os.path.dirname(os.path.abspath(__file__)))

benchmark_args = {
    "wordcount": [
        os.path.abspath("data/generated/random_words.txt.gz")
    ]
}


class Implementation(object):

    def __init__(self, path, language, benchmark_id, benchmark_name, impl_id, impl_name):
        self.path = path
        self.language = language
        self.benchmark_id = int(benchmark_id)
        self.benchmark_name = benchmark_name
        self.impl_id = int(impl_id)
        self.impl_name = impl_name

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

        out_path = os.path.join(
            "results",
            self.language,
            "{:02d}_{}".format(self.benchmark_id, self.benchmark_name),
            "{:02d}_{}".format(self.impl_id, self.impl_name),
            "stdout_run_{:04d}".format(run_id)
        )
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


def discover_implementations():
    impls = []

    implementation_paths = glob.glob('benchmarks/*/*/*')

    for impl_path in implementation_paths:
        m = re.match("benchmarks/(.*)/(\d+)_(.*)/(\d+)_(.*)", impl_path)
        if m is not None:
            language = m.group(1)
            benchmark_id = m.group(2)
            benchmark_name = m.group(3)
            impl_id = m.group(4)
            impl_name = m.group(5)
            print(language, benchmark_name, impl_name)
            impls += [
                Implementation(impl_path, language, benchmark_id, benchmark_name, impl_id, impl_name)
            ]

    return impls


def run_benchmark(impl):
    impl.build()
    args = benchmark_args[impl.benchmark_name]
    impl.run(args, 1)


impls = discover_implementations()
for impl in impls:
    run_benchmark(impl)

