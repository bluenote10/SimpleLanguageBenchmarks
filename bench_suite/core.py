#!/usr/bin/env python

from __future__ import division, print_function

import re
import glob
import subprocess
import time
import random
import datetime

import numpy as np
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .benchmarks.basicmatops import BasicMatOps
from .benchmarks.fibonacci import Fibonacci
from .benchmarks.wordcount import Wordcount

from .utils import *
from .base import Sizes
from .specs import get_system_specs, get_software_specs


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


class Paths(object):

    templates = "templates"
    html = "docs"

    @staticmethod
    def html_benchmark(benchmark_name):
        return os.path.join(
            Paths.html,
            "{:02d}_{}".format(benchmark_id[benchmark_name], benchmark_name),
        )

    @staticmethod
    def html_raw_runtime_csv(benchmark_name, stage_id, stage):
        return os.path.join(
            Paths.html_benchmark(benchmark_name),
            "{:02d}_{}_plot.csv".format(stage_id, stage),
        )

    @staticmethod
    def html_stage_summary_csv(benchmark_name):
        return os.path.join(
            Paths.html_benchmark(benchmark_name),
            "stage_summary.csv",
        )


class BenchmarkEntry(object):

    def __init__(self, language, benchmark_id, benchmark_name, impl_id, impl_name):
        self.language = language
        self.benchmark_id = int(benchmark_id)
        self.benchmark_name = benchmark_name
        self.impl_id = int(impl_id)
        self.impl_name = impl_name
        self.meta_data = self._load_meta_data()

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

        print("Return code: {}".format(p.returncode))
        if p.returncode != 0:
            print_error(
                "Run has failed with return code {}.".format(p.returncode)
            )
            print("STDOUT:\n" + stdout)
            print("STDERR:\n" + stderr)

        elif len(stderr) > 0:
            print_error(
                "Run has return code 0, but returned on STDERR."
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

    def _load_meta_data(self):
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

    @property
    def source_url(self):
        if self.meta_data.get("source-file") is None:
            return None
        else:
            url = self.impl_path + "/" + self.meta_data["source-file"]
            return url

    @property
    def source_description(self):
        return self.meta_data.get("description") or ""

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

    entries.sort(key=lambda x:
        (x.language, x.benchmark_id, x.impl_id, x.impl_path)
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
        b_meta_data = benchmark_meta[b_entry.benchmark_name]
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
        Paths.html + "/*/index.html"
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

        plot_csv = Paths.html_raw_runtime_csv(benchmark_name, stage_id, stage)

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

    plot_csv = Paths.html_stage_summary_csv(benchmark_name)

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

        plot_csv_basename = os.path.basename(Paths.html_raw_runtime_csv(name, stage_id, stage))
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
        impl_locs += [
            (b_entry.language, b_entry.source_url, b_entry.source_description)
        ]

    # compile html
    html_description = markdown.markdown(meta_data.description)

    env = Environment(
        loader=FileSystemLoader(Paths.templates),
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

    out_path = os.path.join(Paths.html_benchmark(name), "index.html")
    with open(out_path, "w") as f:
        f.write(html)


def write_general_summary_csv(affected_benchmarks, all_benchmark_entries):

    runtimes = dict()
    relative_runtimes = dict()
    ranks = dict()

    for benchmark_name in affected_benchmarks:
        benchmark_entries = [
            b_entry for b_entry in all_benchmark_entries
            if b_entry.benchmark_name == benchmark_name
            ]
        meta_data = benchmark_meta[benchmark_name]

        def get_max_runtime(b_entry):
            per_stage_result = meta_data.result_extractor(b_entry)
            return get_median_runtime_of_largest_size(per_stage_result["Total"])

        runtimes_this_benchmark = dict()
        for b_entry in benchmark_entries:
            runtimes_this_benchmark[b_entry] = get_max_runtime(b_entry)

        fastest = min(runtimes_this_benchmark.values())

        # for the time being a quadratic implementation suffices, improve if necessary
        for b_entry in benchmark_entries:
            runtime = runtimes_this_benchmark[b_entry]
            faster_entries = [
                other_entry for other_entry, other_time in runtimes_this_benchmark.iteritems()
                if other_time < runtime
            ]

            # update global dicts
            runtimes[b_entry] = runtime
            ranks[b_entry] = len(faster_entries) + 1
            relative_runtimes[b_entry] = runtime / fastest

    rows = []
    for b_entry in all_benchmark_entries:
        rows += [{
            "benchmark": b_entry.benchmark_name,
            "lang": b_entry.language,
            "descr": b_entry.impl_suffix,
            "url": b_entry.source_url,
            "label": b_entry.language + " (" + b_entry.impl_suffix + ")",
            "time": runtimes[b_entry],
            "relative": relative_runtimes[b_entry],
            "rank": ranks[b_entry],
        }]

    csv_filename = os.path.join(Paths.html, "summary.csv")
    write_csv_with_schema(
        csv_filename, rows,
        schema=["benchmark", "lang", "descr", "url", "label", "time", "relative", "rank"]
    )


def generate_summary_html(affected_benchmarks, all_benchmark_entries):
    print_bold("\nRendering main html")

    write_general_summary_csv(affected_benchmarks, all_benchmark_entries)

    sub_pages = locate_sub_pages(".")

    # load markdown elements and convert to html
    markdown_fragments = load_markdown_fragments(convert_to_html=True)

    env = Environment(
        loader=FileSystemLoader(Paths.templates),
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

    out_path = os.path.join(Paths.html, "index.html")
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
        text = read_file(os.path.join(
            Paths.templates,
            "_{}.md".format(fragment)
        ))
        if convert_to_html:
            text = markdown.markdown(text)
        results[fragment] = text
    return results


def generate_summary_markdown():

    env = Environment(
        loader=FileSystemLoader(Paths.templates),
        undefined=StrictUndefined,
    )
    readme_template = env.get_template("README.md")

    markdown_fragments = load_markdown_fragments()

    readme_text = readme_template.render(
        **markdown_fragments
    )
    write_file("README.md", readme_text)
