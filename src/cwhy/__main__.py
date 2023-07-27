#! /usr/bin/env python3

import argparse
import importlib.metadata
import os
import sys
import tempfile

from . import cwhy


def wrapper(args):
    with open(os.path.join(os.path.dirname(__file__), "wrapper.py.in")) as f:
        template = f.read()
    return template.format(compiler=args["wrapper_compiler"], args=args)


def main():
    parser = argparse.ArgumentParser(
        prog="cwhy",
        description="CWhy explains and fixes compiler diagnostic errors.",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="print the version of cwhy and exit",
    )

    parser.add_argument(
        "--llm",
        type=str,
        default="gpt-3.5-turbo",
        help="the language model to use, e.g., 'gpt-3.5-turbo' or 'gpt-4' (default: gpt-3.5-turbo)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="timeout for API calls in seconds (default: 60)",
    )
    parser.add_argument(
        "--max-context",
        type=int,
        default=30,
        help="maximum number of context to use (default: 30)",
    )

    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="only print prompt and exit (for debugging purposes)",
    )
    parser.add_argument(
        "--wrapper",
        action="store_true",
        help="enable compiler wrapper behavior",
    )
    parser.add_argument(
        "--wrapper-compiler",
        metavar="COMPILER",
        type=str,
        default="c++",
        help="the underlying compiler. Only enabled with --wrapper",
    )

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    subparsers.add_parser("explain", help="explain the diagnostic (default)")
    subparsers.add_parser("fix", help="propose a fix for the diagnostic")
    subparsers.add_parser(
        "extract-sources", help="extract the source locations from the diagnostic"
    )

    parser.set_defaults(subcommand="explain")

    args = vars(parser.parse_args())

    if args["wrapper"]:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(wrapper(args))
        # NamedTemporaryFiles are not executable by default. Set its mode to 755 here with an octal literal.
        os.chmod(f.name, 0o755)
        print(f.name)
    elif args["version"]:
        print(f"cwhy version {importlib.metadata.metadata('cwhy')['Version']}")
    else:
        stdin = sys.stdin.read()
        if stdin:
            cwhy.evaluate(args, stdin)
