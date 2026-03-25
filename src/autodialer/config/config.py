import os
import dotenv

dotenv.load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value


PANEL_PASSWORD: str = _require_env("PANEL_PASSWORD")
PPPOE_USERNAME: str = _require_env("PPPOE_USERNAME")
PPPOE_PASSWORD: str = _require_env("PPPOE_PASSWORD")
ASN: str | None = os.getenv("ASN") or None
