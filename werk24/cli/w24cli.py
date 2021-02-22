""" Command Line Interface for W24
"""
import argparse
import asyncio
from dotenv import load_dotenv
import werk24.cli.techread
import werk24.cli.auth

load_dotenv(".werk24")


def main() -> None:
    parser = argparse.ArgumentParser(prog="w24cli")
    subparsers = parser.add_subparsers(
        dest="command",
        help="Subcommand. Currently supported: techread")
    subparsers.required = True

    parser_techread = subparsers.add_parser(
        "techread",
        help="Submit a Technical Drawing to Werk24 for analysis")

    parser_techread.add_argument(
        "input_file",
        help="path to the file that is to be analyzed")

    parser_techread.add_argument(
        "--ask-techread-started",
        help="ask for a callback when the techread process has been picked up by a worker",  # noqa
        action="store_true")

    parser_techread.add_argument(
        "--ask-page-thumbnail",
        help="ask for a thumbnail for each page in the document",
        action="store_true")

    parser_techread.add_argument(
        "--ask-sheet-thumbnail",
        help="ask for a thumbnail of each sheet in the document",
        action="store_true")

    parser_techread.add_argument(
        "--ask-canvas-thumbnail",
        help="ask for a thumbnail of each canvas in the document",
        action="store_true")

    parser_techread.add_argument(
        "--ask-sectional-thumbnail",
        help="ask for a thumbnail of each sectional of each sheet in the document",  # noqa
        action="store_true")

    parser_techread.add_argument(
        "--ask-variant-angles",
        help="ask for the angles of each variant",  # noqa
        action="store_true")

    parser_techread.add_argument(
        "--ask-variant-measures",
        help="ask for the measures of each variant",  # noqa
        action="store_true")

    parser_techread.add_argument(
        "--ask-variant-gdts",
        help="ask for the GD&Ts of each variant",  # noqa
        action="store_true")

    parser_techread.add_argument(
        "--ask-variant-leaders",
        help="ask for the Leaders of each variant",  # noqa
        action="store_true")

    parser_techread.add_argument(
        "--ask-variant-cad",
        help="ask for the CAD file of each variant",  # noqa
        action="store_true")

    parser_auth = subparsers.add_parser(
        "auth",
        help="Interact with the authentication service")

    parser_auth.add_argument(
        '--ask-jwt-token',
        help="Obtain a valid JWT token",
        action="store_true")

    args = parser.parse_args()
    if args.command == "techread":
        asyncio.run(werk24.cli.techread.main(args))

    elif args.command == "auth":
        asyncio.run(werk24.cli.auth.main(args))


if __name__ == "__main__":
    main()
