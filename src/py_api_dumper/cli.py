# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

import argparse
import sys
from pathlib import Path

from . import APIDiff, APIDump


def dump(args):

    # Dump module APIs
    dump = APIDump.from_modules(*args.modules)

    if args.output is None:

        # Print API dump as text to standard output
        dump.print_as_text()

    elif args.text:

        # Print API dump as text to the given --output file
        dump.print_as_text(args.output.open("wt"))

    else:

        # Save the API dump to the given --output file in a reloadable format
        dump.save_to_file(args.output)


def diff(args):

    # Load API diff
    diff = APIDiff.from_files(args.old_dump, args.new_dump)

    if args.output is None:

        # Print API diff as text to standard output
        diff.print_as_text()

    elif args.text:

        # Print API diff as text to the given --output file
        diff.print_as_text(args.output.open("wt"))

    else:

        # Save the API diff to the given --output file in JSON format
        diff.save_as_json(args.output)


def cli(*argv):

    # Build command-line argument parser
    parser = argparse.ArgumentParser(
        description="Python API dumping and comparison tool"
    )
    subparsers = parser.add_subparsers(help="sub-commands")
    parser_dump = subparsers.add_parser(
        "dump", description="dump APIs", help="dump APIs"
    )
    parser_dump.add_argument(
        "-o", "--output", type=Path, default=None, help="Output API dump to this file"
    )
    parser_dump.add_argument(
        "-t", "--text", action="store_true", help="Output API dump in text format"
    )
    parser_dump.add_argument(
        "modules", type=str, nargs="+", help="Dump APIs of these modules"
    )
    parser_dump.set_defaults(subcommand=dump)
    parser_diff = subparsers.add_parser(
        "diff", description="compare APIs", help="compare APIs"
    )
    parser_diff.add_argument(
        "-o", "--output", type=Path, default=None, help="Output API diff to this file"
    )
    parser_diff.add_argument(
        "-t", "--text", action="store_true", help="Output API diff in text format"
    )
    parser_diff.add_argument(
        "old_dump", type=Path, help="File containing dump of old API"
    )
    parser_diff.add_argument(
        "new_dump", type=Path, help="File containing dump of new API"
    )
    parser_diff.set_defaults(subcommand=diff)

    # Parse command line
    argv = [str(a) for a in (argv or sys.argv[1:] or ["--help"])]
    args = parser.parse_args(argv)

    # Execute sub-command
    try:
        args.subcommand(args)
    except BrokenPipeError:  # pragma: no cover
        pass
