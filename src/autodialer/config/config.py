import os
import dotenv  # type: ignore[import-not-found]
import logging

logger = logging.getLogger(__name__)


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
