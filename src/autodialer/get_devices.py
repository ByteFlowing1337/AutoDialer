import logging
import sys
import argparse
from autodialer.routers import get_router


logger = logging.getLogger(__name__)


def print_devices_table(devices: list) -> None:
    if not devices:
        print("No devices connected.")
        return

    header = f"{'HOSTNAME':25} {'IP':15} {'MAC':18} {'TYPE':9} {'UP':>6} {'DOWN':>6} {'ME':>3}"

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
            color = GREEN if is_me else RESET
            me_marker = f"{GREEN}  Y{RESET}" if is_me else f"{RED}  N{RESET}"

            print(
                f"{color}{d['hostname'][:25]:25}{RESET} "
                f"{YELLOW}{d['ip'][:15]:15}{RESET} "
                f"{d['mac'][:18]:18} "
                f"{d['type'][:9]:9} "
                f"{d['up_kbps']:>6} "
                f"{d['down_kbps']:>6} "
                f"{me_marker}"
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
                f"{me_marker:>3}"
            )


def get_devices() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(
        description="Get connected devices from the router."
    )
    parser.add_argument(
        "-e",
        "--env",
        action="append",
        help="Set environment variables (e.g., -e PANEL_PASSWORD=secret)",
    )
    args = parser.parse_args()
    if args.env:
        from autodialer.config import parse_and_save_env_flags

        parse_and_save_env_flags(args.env)

    router = get_router()
    if router is None:
        logger.error("Unsupported or undetected router vendor.")
        sys.exit(1)
    devices = router.get_connected_devices()
    print_devices_table(devices)


if __name__ == "__main__":
    get_devices()
