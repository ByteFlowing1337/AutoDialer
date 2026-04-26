import os
import dotenv  # type: ignore[import-not-found]
import logging

file_name = ".env.example" if not os.path.exists(".env") else ".env"
if file_name == ".env.example":
    logging.warning(
        "Warning: .env file not found. Using .env.example as fallback."
        "Please create a .env file with the necessary environment variables."
    )
env_file = dotenv.find_dotenv(filename=file_name)
dotenv.load_dotenv(env_file)

logger = logging.getLogger(__name__)

PANEL_USERNAME: str = os.getenv("PANEL_USERNAME") or "admin"

_PANEL_PASSWORD: str | None = os.getenv("PANEL_PASSWORD")
if _PANEL_PASSWORD is None:
    logger.error("Error: PANEL_PASSWORD environment variable is not set.")
    exit(1)

PANEL_PASSWORD: str = _PANEL_PASSWORD
PPPOE_USERNAME: str | None = os.getenv("PPPOE_USERNAME") or None
PPPOE_PASSWORD: str | None = os.getenv("PPPOE_PASSWORD") or None
ASN: str | None = os.getenv("ASN") or None
