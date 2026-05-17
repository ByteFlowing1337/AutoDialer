import sys


# Lazy import wrapper
class _Ansi:
    def __init__(self, code: str) -> None:
        self._code = code

    def __str__(self) -> str:
        return self._code if sys.stdout.isatty() else ""

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return str(self) == other

    def __format__(self, spec: str) -> str:
        return format(str(self), spec)


CYAN = _Ansi("\033[96m")
GREEN = _Ansi("\033[92m")
YELLOW = _Ansi("\033[93m")
RED = _Ansi("\033[91m")
RESET = _Ansi("\033[0m")
