import logging
from pathlib import Path
from sys import argv
from autodialer.routers.get_vendor_api import get_vendor_api


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


def get_devices() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    match len(argv):
        case 1:
            Vendor = get_vendor_api()
            router = Vendor() if Vendor is not None else None
            if router is None:
                logger.error("No router API available to fetch connected devices.")
                exit(1)
            devices = router.get_connected_devices()
            print_devices_table(devices)
        case _:
            if len(argv) > 1:
                logger.error("Unknown argument: %s", argv[1])
            if Path(argv[0]).suffix.lower() == ".py":
                logger.error("Usage: python get_devices.py")
            else:
                logger.error("Usage: autodialer-devices")
            exit(1)


if __name__ == "__main__":
    get_devices()
