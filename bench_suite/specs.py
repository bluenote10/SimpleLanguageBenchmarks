#!/usr/bin/env python

from __future__ import division, print_function

import re
import subprocess
import platform

from .utils import print_warn


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

