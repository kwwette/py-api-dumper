import argparse
import sys
from pathlib import Path

from . import APIDump


def dump(args):

    # Dump module APIs
    dump = APIDump.from_modules(*args.modules)

    if args.output is None:

        # Print API dump as text to standard output
        dump.print_as_text()

    elif args.text:

        # Print API dump as text to the given --output file
        dump.print_as_text(to=args.output.open("w"))


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

    # Parse command line
    argv = [str(a) for a in (argv or sys.argv[1:] or ["--help"])]
    args = parser.parse_args(argv)

    # Execute sub-command
    args.subcommand(args)
