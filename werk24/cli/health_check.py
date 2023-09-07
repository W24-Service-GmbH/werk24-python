import argparse
import platform
import sys
from datetime import datetime
import os.path
import websockets
from websockets.exceptions import InvalidStatusCode
from werk24.cli import utils
import werk24
from werk24.techread_client import LicenseError

LINE_LENGTH = 80
URI = "wss://ws-api.w24.co/v2"


async def main(args: argparse.Namespace) -> None:
    """
    Perform the Health Checks.
    Args:
        args (argparse.Namespace): Command-line arguments.
    """
    print_section("System Information", get_system_info())
    print_section("License Information", get_license_info())
    print_section("Module Information", get_module_info())
    print_section("Network Information", await get_network_info())
    print_section("Miscellaneous", get_misc_info())


def print_section(headline: str, information: dict) -> None:
    """
    Print a section with given headline and information.
    Args:
        headline (str): The headline of the section.
        information (dict): A dictionary containing the information to be printed.
    """
    filler = max(0, LINE_LENGTH - 9 - len(headline))
    print("\n{0} [{1}] {2}".format("-" * 5, headline, "-" * filler))
    for caption, value in information.items():
        print("{0:<30}: {1}".format(caption, value))
    print("-" * LINE_LENGTH)


def get_system_info() -> dict:
    """Get system information.
    Returns:
        dict: A dictionary containing the system information.
    """
    return {
        "OS": f"{platform.system()} {platform.release()}",
        "Python Version": sys.version,
    }


def get_license_info() -> dict:
    """Get the license Information

    Returns:
    -------
    dict: A dictionary containing the license information.
    """
    try:
        client = utils.make_client()

    except LicenseError:
        return {"License Information": "NOT FOUND"}

    return {
        "License Information": "FOUND",
        "Username": client._auth_client.username,
    }


def get_module_info() -> dict:
    """Get module information.
    Returns:
        dict: A dictionary containing the module information.
    """
    return {
        "Werk24 Version": werk24.__version__,
    }


async def get_network_info() -> dict:
    """Test connection and get network info.
    Returns:
        dict: A dictionary containing the results of the connection test.
    """
    try:
        async with websockets.connect(URI):
            return {"ws-api.w24.co Connection": "Successful"}
    except InvalidStatusCode as e:
        if e.status_code == 401:
            return {"Websocket Connection": "Successful, Unauthorized"}
        else:
            return {"Websocket Connection": f"Unsuccessful: {str(e.status_code)}"}
    except Exception as e:
        return {"Websocket Connection": f"Unsuccessful: {type(e)}, {e}"}


def get_misc_info() -> dict:
    def _check_werk24_name_conflict() -> str:
        if os.path.exists("werk24.py"):
            return "! NAME CONFLICT ! Please rename your werk24.py file"
        else:
            return "No Conflict"

    return {
        "Time": datetime.now(),
        "Werk24 Name Conflict": _check_werk24_name_conflict(),
    }
