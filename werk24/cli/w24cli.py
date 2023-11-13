""" Command Line Interface for W24
"""
import argparse
import asyncio

import werk24.cli.auth
import werk24.cli.health_check
import werk24.cli.support
import werk24.cli.techread


def main() -> None:
    parser = argparse.ArgumentParser(prog="w24cli")
    subparsers = parser.add_subparsers(
        dest="service", help="Service. Currently supported: techread, auth, support"
    )
    subparsers.required = True

    _add_auth_parser(subparsers)
    _add_support_parser(subparsers)
    _add_techread_parser(subparsers)

    args = parser.parse_args()
    if args.service == "techread":
        asyncio.run(werk24.cli.techread.main(args))

    elif args.service == "auth":
        asyncio.run(werk24.cli.auth.main(args))

    elif args.service == "support":
        asyncio.run(werk24.cli.support.main(args))

    elif args.service == "health_check":
        asyncio.run(werk24.cli.health_check.main(args))


def _add_support_parser(subparsers):
    support_parser = subparsers.add_parser("support", help="Support Service")

    support_subparsers = support_parser.add_subparsers(
        dest="command",
        help="Command. Currently supported: create-helpdesk-task",
        required=True,
    )

    create_parser = support_subparsers.add_parser(
        "create-helpdesk-task", help="Create a new help desk task"
    )

    create_parser.add_argument("--request-id", action="store", required=True)

    create_parser.add_argument("--observed-outcome", action="store", required=True)

    create_parser.add_argument("--expected-outcome", action="store", required=True)

    create_parser.add_argument("--comment", action="store")

    create_parser.add_argument("--importance", action="store", required=True)


def _add_auth_parser(subparsers):
    parser_auth = subparsers.add_parser(
        "auth", help="Interact with the authentication service"
    )

    parser_auth.add_argument(
        "--ask-jwt-token", help="Obtain a valid JWT token", action="store_true"
    )


def _add_techread_parser(subparsers):
    parser_techread = subparsers.add_parser(
        "techread", help="Submit a Technical Drawing to Werk24 for analysis"
    )

    parser_techread.add_argument(
        "input_file", help="path to the file that is to be analyzed"
    )

    parser_techread.add_argument(
        "--sub-account",
        help="Sub-Account that the request should be attributed to.",
        action="store",
        dest="sub_account",
        default=None,
    )

    parser_techread.add_argument(
        "--ask-techread-started",
        help="ask for a callback when the techread process has been picked up by a worker",  # noqa
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-page-thumbnail",
        help="ask for a thumbnail for each page in the document",
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-sheet-thumbnail",
        help="ask for a thumbnail of each sheet in the document",
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-sheet-anonymization",
        help="ask for an anonymized of each sheet in the document",
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-canvas-thumbnail",
        help="ask for a thumbnail of each canvas in the document",
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-sectional-thumbnail",
        help="ask for a thumbnail of each sectional of each sheet in the document",  # noqa
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-variant-cad",
        help="ask for the CAD file of each variant",  # noqa
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-variant-external-dimensions",
        help="ask for the External Dimensions of each variant",  # noqa
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-variant-gdts",
        help="ask for the GD&Ts of each variant",  # noqa
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-variant-measures",
        help="ask for the measures of each variant",  # noqa
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-variant-roughnesses",
        help="ask for the Surface Roughnesses of each variant",  # noqa
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-variant-radii",
        help="ask for the Radii of each variant",  # noqa
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-variant-thread-elements",
        help="ask for the Thread Elements",  # noqa
        action="store_true",
    )

    parser_techread.add_argument(
        "--ask-titleblock", help="ask for the Title Block", action="store_true"  # noqa
    )

    parser_techread.add_argument(
        "--ask-part-family-characterization",
        help="ask for the Part Family Characterization",  # noqa
        action="store",
        dest="part_family_id",
    )

    parser_techread.add_argument(
        "--ask-debug",
        help="internal debug option",
        action="store",
        dest="debug_key",
    )

    parser_health_check = subparsers.add_parser(
        "health_check", help="Perform Health Checks"
    )
    parser_health_check.add_argument("type", help="Type of Health Check to perform")


if __name__ == "__main__":
    main()
