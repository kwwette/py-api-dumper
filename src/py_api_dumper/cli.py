import argparse
import sys
from pathlib import Path

from . import APIDump


def dump(args):

    # Dump module APIs
    dump = APIDump.from_modules(args.modules)

    if args.output is None:

        # Print API dump to standard output
        dump.print_as_text()


def cli(*argv: str):

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
        "modules", type=str, nargs="+", help="Dump APIs of these modules"
    )
    parser_dump.set_defaults(subcommand=dump)

    # Parse command line
    parse_argv = list(argv)
    if len(parse_argv) == 0:
        parse_argv = sys.argv[1:]
    if len(parse_argv) == 0:
        parse_argv = ["--help"]
    args = parser.parse_args(parse_argv)

    # Execute sub-command
    args.subcommand(args)
