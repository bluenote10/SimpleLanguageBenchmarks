#!/usr/bin/env python

from __future__ import division, print_function

import os
import errno


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
