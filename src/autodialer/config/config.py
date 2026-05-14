import os
import sys
import dotenv
import logging
from pathlib import Path
import tempfile
from collections import namedtuple

logger = logging.getLogger(__name__)

APP_NAME = "AutoDialer"


def _safe_home_dir() -> Path:
    try:
        return Path.home()
    except RuntimeError:
        fallback_dir = (
            os.getenv("HOME")
            or os.getenv("USERPROFILE")
            or os.getenv("TEMP")
            or tempfile.gettempdir()
        )
        return Path(fallback_dir)


def _default_config_dir() -> Path:
    if sys.platform.startswith("win"):
        base = os.getenv("APPDATA")
        if base:
            return Path(base) / APP_NAME
        return _safe_home_dir() / "AppData" / "Roaming" / APP_NAME
    elif sys.platform == "linux":
        return _safe_home_dir() / ".config" / APP_NAME.lower()
    elif sys.platform == "darwin":
        return _safe_home_dir() / "Library" / "Application Support" / APP_NAME
    return _safe_home_dir() / ".config" / APP_NAME.lower()


def get_env_file_path() -> Path:
    config_dir = Path(os.getenv("AUTODIALER_CONFIG_DIR") or _default_config_dir())
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / ".env"


def parse_and_save_env_flags(env_args: list[str]):
    """Saves passed KEY=VALUE strings to .env and the current environment."""

    env_file_path = get_env_file_path()

    # Create an empty .env file if it doesn't exist so python-dotenv doesn't complain
    if not env_file_path.exists():
        env_file_path.touch()

    for item in env_args:
        if "=" not in item:
            logger.error(
                "Error: -e/--env requires a KEY=VALUE argument (e.g., -e PANEL_PASSWORD=secret)."
            )
            sys.exit(1)

        key, value = item.split("=", 1)
        if not value:
            logger.error(
                "Error: -e/--env requires a KEY=VALUE argument (e.g., -e PANEL_PASSWORD=secret)."
            )
            sys.exit(1)

        # Write the key-value pair to the .env file
        dotenv.set_key(str(env_file_path), key, value)

        # Update the current environment immediately
        os.environ[key] = value


def load_env_file():
    env_file = get_env_file_path()
    if not env_file.exists():
        logger.warning(
            f".env file not found at {env_file}. Please create it or set values via -e."
        )
        env_file.touch()  # Create an empty .env file to avoid issues with dotenv
    dotenv.load_dotenv(str(env_file))

    # For some routers, username is not required, so we can default to "admin".
    PANEL_USERNAME: str = os.getenv("PANEL_USERNAME") or "admin"

    # Password is required for all routers, so we will exit if it's not set.
    _PANEL_PASSWORD: str | None = os.getenv("PANEL_PASSWORD")
    if _PANEL_PASSWORD is None:
        logger.error("Error: PANEL_PASSWORD environment variable is not set.")
        sys.exit(1)

    PANEL_PASSWORD: str = _PANEL_PASSWORD
    PPPOE_USERNAME: str | None = os.getenv("PPPOE_USERNAME") or None
    PPPOE_PASSWORD: str | None = os.getenv("PPPOE_PASSWORD") or None
    ASN: str | None = os.getenv("ASN") or None
    EnvVars = namedtuple(
        "EnvVars",
        ["PANEL_USERNAME", "PANEL_PASSWORD", "PPPOE_USERNAME", "PPPOE_PASSWORD", "ASN"],
    )
    return EnvVars(PANEL_USERNAME, PANEL_PASSWORD, PPPOE_USERNAME, PPPOE_PASSWORD, ASN)
