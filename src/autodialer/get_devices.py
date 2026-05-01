import logging
from pathlib import Path
from sys import argv
from autodialer.routers.get_router import get_router


logger = logging.getLogger(__name__)


def print_devices_table(devices: list) -> None:
    if not devices:
        print("No devices connected.")
        return
    header = f"{'HOSTNAME':25} {'IP':15} {'MAC':18} {'TYPE':9} {'UP':>6} {'DOWN':>6} {'ME':>3}"
    print(header)
    print("-" * len(header))
    for d in devices:
        print(
            f"{d['hostname'][:25]:25} "
            f"{d['ip'][:15]:15} "
            f"{d['mac'][:18]:18} "
            f"{d['type'][:9]:9} "
            f"{d['up_kbps']:>6} "
            f"{d['down_kbps']:>6} "
            f"{'Y' if d['is_current'] else 'N':>3}"
        )


def validate_args(args: list[str]) -> bool:
    if len(args) == 1:
        return True
    logger.error("Unknown argument: %s", args[1])
    if Path(args[0]).suffix.lower() == ".py":
        logger.error("Usage: python get_devices.py")
    else:
        logger.error("Usage: autodialer-devices")
    return False


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if not validate_args(argv):
        exit(1)
    router = get_router()
    if not router:
        logger.error("Unsupported or undetected router vendor.")
        exit(1)
    devices = router.get_connected_devices()
    print_devices_table(devices)


if __name__ == "__main__":
    main()
