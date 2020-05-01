import sys
import argparse

import pyc2e
from pyc2e.common import SCRIPT_START_STRING_REGEX

root_parser = argparse.ArgumentParser(prog="pyc2e")
subparsers = root_parser.add_subparsers(title="commands", dest="command")

inject_parser = subparsers.add_parser(
    "inject", aliases=['inj'], prog="inject"
)

inject_parser.add_argument(
    '-a', "--add-script",
    type=bool,
    default=False,
)

injection_source_group = inject_parser.add_mutually_exclusive_group()
injection_source_group.add_argument(
    "--file",
    type=argparse.FileType('r', encoding='UTF-8'), default='-'
)
injection_source_group.add_argument(
    '--caos',
    type=str,
)

# check if stderr exists for printing
# yes, it does

#exit return value


def inject_from(
    args
) -> None:
    """
    Inject CAOS from a stream or string source.

    """

    data = args.caos or args.file.read()
    response = None
    if SCRIPT_START_STRING_REGEX.match(data):
        response = pyc2e.execute_caos(data)
    else:
        response = pyc2e.execute_caos(data)
        print(response.text)


def main() -> None:
    args = root_parser.parse_args()
    if args.command == "inject":
        inject_from(args)





