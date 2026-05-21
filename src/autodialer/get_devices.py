import sys

from autodialer.network.get_router import get_router


def get_devices() -> list:
    router = get_router()
    if router is None:
        raise RuntimeError("Unable to detect router vendor or no API available.")
    devices = router.get_connected_devices()
    return devices


def print_devices_table() -> None:
    devices = get_devices()
    if not devices:
        print("No devices connected.")
        return

    header = (
        f"{'HOSTNAME':25} {'IP':15} {'MAC':18} {'TYPE':9} "
        f"{'UP':>6} {'DOWN':>6} {'ME':>3}"
    )

    if sys.stdout.isatty():
        # Standard terminal ANSI color codes
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        RESET = "\033[0m"
        # Print header in CYAN and highlight the current device in GREEN
        print(f"{CYAN}{header}{RESET}")
        print("-" * len(header))
        for d in devices:
            is_me = d["is_current"]

            # Determine the color and the 'ME' marker based on 'is_current'
            is_me_color = GREEN if is_me else RED
            me_marker = "Y" if is_me else "N"

            print(
                f"{is_me_color}{d['hostname'][:25]:25}{RESET} "
                f"{YELLOW}{d['ip'][:15]:15}{RESET} "
                f"{d['mac'][:18]:18} "
                f"{d['type'][:9]:9} "
                f"{d['up_kbps']:>6} "
                f"{d['down_kbps']:>6} "
                f"{is_me_color}{me_marker:>2}{RESET}"
            )
    else:
        print(header)
        print("-" * len(header))
        for d in devices:
            is_me = d["is_current"]
            me_marker = "Y" if is_me else "N"
            print(
                f"{d['hostname'][:25]:25} "
                f"{d['ip'][:15]:15} "
                f"{d['mac'][:18]:18} "
                f"{d['type'][:9]:9} "
                f"{d['up_kbps']:>6} "
                f"{d['down_kbps']:>6} "
                f"{me_marker:>2}"
            )
