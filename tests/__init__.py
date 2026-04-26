from pathlib import Path
import sys
import atexit
import os
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Keep tests independent from local .env files.
os.environ.setdefault("PANEL_PASSWORD", "test-panel-password")

_DOTENV_PATCHERS = [
    patch("dotenv.find_dotenv", return_value=".env.mock"),
    patch("dotenv.load_dotenv", return_value=True),
]

for _patcher in _DOTENV_PATCHERS:
    _patcher.start()


def _stop_dotenv_patchers() -> None:
    for _patcher in reversed(_DOTENV_PATCHERS):
        _patcher.stop()


atexit.register(_stop_dotenv_patchers)
