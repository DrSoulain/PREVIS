import sys
from argparse import ArgumentParser
from typing import List
from typing import Optional

from previs._cli.commands import perform_search
from previs._cli.commands import perform_survey


def main(argv: Optional[List[str]] = None) -> int:
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    search_parser = subparsers.add_parser(
        "search", help="Search and fetch data from the VO"
    )

    # INPUT and OUTPUT directory
    # __________________________________________________________________________

    search_parser.add_argument(
        "-t",
        "--target",
        help="Name of the target",
    )

    search_parser.add_argument(
        "--save_to",
        default=None,
        type=str,
        help="If save_to is set, figures and fetched data are saved.",
    )

    search_parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="If True, update MATISSE performances on the ESO website.",
    )

    search_parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="Plot figures.",
    )

    search_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print informations.",
    )

    survey_parser = subparsers.add_parser(
        "survey", help="Search and fetch data from the VO of a list of target"
    )
    survey_parser.add_argument(
        "-t",
        "--target",
        nargs="+",
        default=[],
        type=str,
        help="List of the targets",
    )
    survey_parser.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="Plot figures.",
    )
    survey_parser.add_argument(
        "--save_to",
        default=None,
        type=str,
        help="If save_to is set, figures and fetched data are saved.",
    )

    args = parser.parse_args(argv)

    retv = 1
    if args.command == "search":
        retv = perform_search(args)
    elif args.command == "survey":
        retv = perform_survey(args)
    return retv


if __name__ == "__main__":
    sys.exit(main())
