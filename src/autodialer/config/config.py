import os
import dotenv  # type: ignore[import-not-found]
import logging

logger = logging.getLogger(__name__)


env_file = dotenv.find_dotenv()
if env_file == "":
    raise RuntimeError("No .env file found! Please create one at root directory.")
dotenv.load_dotenv(env_file)


PANEL_USERNAME: str = os.getenv("PANEL_USERNAME") or "admin"

_PANEL_PASSWORD: str | None = os.getenv("PANEL_PASSWORD")
if _PANEL_PASSWORD is None:
    logger.error("Error: PANEL_PASSWORD environment variable is not set.")
    raise RuntimeError("Error: PANEL_PASSWORD environment variable is not set.")

PANEL_PASSWORD: str = _PANEL_PASSWORD
PPPOE_USERNAME: str | None = os.getenv("PPPOE_USERNAME") or None
PPPOE_PASSWORD: str | None = os.getenv("PPPOE_PASSWORD") or None
ASN: str | None = os.getenv("ASN") or None
