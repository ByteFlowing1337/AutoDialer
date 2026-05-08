import os
import sys
import dotenv
import logging
from pathlib import Path
from collections import namedtuple

logger = logging.getLogger(__name__)


def parse_and_save_env_flags():
    """Extracts -e / --env flags, saves them to .env, and removes them from sys.argv"""

    env_file_path = Path(".env")

    # Create an empty .env file if it doesn't exist so python-dotenv doesn't complain
    if not env_file_path.exists():
        env_file_path.touch()

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] in ("-e", "--env"):
            if i + 1 < len(sys.argv) and "=" in sys.argv[i + 1]:
                key, value = sys.argv[i + 1].split("=", 1)

                # Write the key-value pair to the .env file
                dotenv.set_key(str(env_file_path), key, value)

                # Update the current environment immediately
                os.environ[key] = value

                # Remove the parsed arguments from sys.argv
                sys.argv.pop(i)
                sys.argv.pop(i)
            else:
                logger.error(
                    "Error: -e/--env requires a KEY=VALUE argument (e.g., -e PANEL_PASSWORD=secret)."
                )
                sys.exit(1)
        else:
            i += 1


def load_env_file():
    env_file = dotenv.find_dotenv()
    if env_file == "":
        logger.error(
            ".env file not found. Please create a .env file with appropriate values."
        )
        exit(1)
    dotenv.load_dotenv(env_file)

    # For some routers, username is not required, so we can default to "admin".
    PANEL_USERNAME: str = os.getenv("PANEL_USERNAME") or "admin"

    # Password is required for all routers, so we will exit if it's not set.
    _PANEL_PASSWORD: str | None = os.getenv("PANEL_PASSWORD")
    if _PANEL_PASSWORD is None:
        logger.error("Error: PANEL_PASSWORD environment variable is not set.")
        exit(1)

    PANEL_PASSWORD: str = _PANEL_PASSWORD
    PPPOE_USERNAME: str | None = os.getenv("PPPOE_USERNAME") or None
    PPPOE_PASSWORD: str | None = os.getenv("PPPOE_PASSWORD") or None
    ASN: str | None = os.getenv("ASN") or None
    EnvVars = namedtuple(
        "EnvVars",
        ["PANEL_USERNAME", "PANEL_PASSWORD", "PPPOE_USERNAME", "PPPOE_PASSWORD", "ASN"],
    )
    return EnvVars(PANEL_USERNAME, PANEL_PASSWORD, PPPOE_USERNAME, PPPOE_PASSWORD, ASN)
