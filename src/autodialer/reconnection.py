import logging
from sys import argv
from pathlib import Path
from typing import Literal

from autodialer.routers.base_router_api import RouterAPI
from autodialer.network.check_isp import check_isp_with_retries
from autodialer.network.is_target_asn import is_target_asn, normalize_asn
from autodialer.routers.get_vendor_api import get_vendor_api
from autodialer.network.get_ip_address import get_ip_address
from autodialer.network.wait_internet_recovery import wait_internet_recovery


logger = logging.getLogger(__name__)


class Reconnection:
    def __init__(self, router: RouterAPI, delay: int = 30, max_attempts: int = 5):
        self.router = router
        self.max_attempts = max_attempts
        # Delay in seconds between reconnection attempts,
        # ensuring public(ISP's) DHCP leases have time to expire and new IPs to be assigned
        self.delay = delay

    def _get_wan_proto(self) -> str | None:
        return self.router.get_wan_proto()

    def _apply_reconnection(self, proto: str) -> bool:
        if proto == "pppoe":
            return self.router.make_pppoe_reconnection()
        if proto == "dhcp":
            return self.router.dhcp_renew()

        logger.error("Unsupported WAN protocol: %s", proto)
        return False

    def run_reconnection(
        self, mode: Literal["force", "asn", "change"], *, asn: str | None
    ) -> None:

        proto = self._get_wan_proto()

        if proto is None:
            logger.error("Unable to determine current WAN protocol.")
            exit(1)

        match mode:
            case "force":
                if not self._apply_reconnection(proto):
                    exit(1)

                wait_internet_recovery()

                isp = check_isp_with_retries()
                ip = get_ip_address()
                if isp and ip is not None:
                    logger.info("IP info after forced reconnection: %s %s", ip, isp)
                else:
                    logger.warning(
                        "Forced reconnection completed, but unable to fetch IP info."
                    )
                return

            case "change":
                if (current_ip := get_ip_address()) is None:
                    logger.error("Unable to fetch current IP address. Exiting.")
                    exit(1)

                after_reconnection_ip: str | None = current_ip
                attempts = 0

                while (
                    current_ip == after_reconnection_ip
                ) and attempts < self.max_attempts:
                    if not self._apply_reconnection(proto):
                        exit(1)

                    wait_internet_recovery()

                    if (after_reconnection_ip := get_ip_address()) is None:
                        logger.error(
                            "Unable to fetch IP address after reconnection. Exiting."
                        )
                        exit(1)
                    attempts += 1

                if current_ip != after_reconnection_ip:
                    isp = check_isp_with_retries()
                    logger.info(
                        "IP info after reconnection: %s -> %s %s",
                        current_ip,
                        after_reconnection_ip,
                        isp,
                    )
                    return
                logger.error(
                    "Failed to change IP address after %d attempts.", self.max_attempts
                )
                exit(1)

            case "asn":
                for _ in range(self.max_attempts):
                    if not self._apply_reconnection(proto):
                        exit(1)

                    wait_internet_recovery()

                    isp = check_isp_with_retries()
                    if isp is None:
                        exit(1)

                    if is_target_asn(current_isp=isp, target_asn=asn):
                        return

                logger.error(
                    "Reached maximum reconnection attempts without switching to the desired ASN."
                )
                exit(1)

    def main(self) -> None:
        match argv[1]:
            case "-f" | "--force":
                self.run_reconnection(mode="force", asn=None)
            case "-a" | "--asn":
                self.run_reconnection(mode="asn", asn=argv[2])
            case "-c" | "--change":
                self.run_reconnection(mode="change", asn=None)
            case _:
                logger.error("Unknown argument: %s", argv[1])
                if Path(argv[0]).suffix.lower() == ".py":
                    logger.error(
                        "Usage: python reconnection.py [-f|--force] [-a|--asn <ASN>] [-c|--change]"
                    )
                else:
                    logger.error(
                        "Usage: autodialer [-f|--force] [-a|--asn <ASN>] [-c|--change]"
                    )
                exit(1)


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(argv) < 2:
        logger.error("No reconnection mode specified.")
        if Path(argv[0]).suffix.lower() == ".py":
            logger.info(
                "Usage: python reconnection.py [-f|--force] [-a|--asn <ASN>] [-c|--change]"
            )
        else:
            logger.info("Usage: autodialer [-f|--force] [-a|--asn <ASN>] [-c|--change]")
        exit(1)

    if argv[1] in ("-h", "--help") or argv[1] not in (
        "-f",
        "--force",
        "-a",
        "--asn",
        "-c",
        "--change",
    ):
        if argv[1] not in ("-h", "--help"):
            logger.error("No reconnection mode specified.")
        if Path(argv[0]).suffix.lower() == ".py":
            logger.info(
                "Usage: python reconnection.py [-f|--force] [-a|--asn <ASN>] [-c|--change]"
            )
        else:
            logger.info("Usage: autodialer [-f|--force] [-a|--asn <ASN>] [-c|--change]")
        exit(1)
    if argv[1] in ("-a", "--asn") and (len(argv) < 3 or normalize_asn(argv[2]) == ""):
        logger.error(
            "ASN parameter is required when using the -a or --asn flag. e.g. AS12345"
        )
        exit(1)
    if argv[1] in ("-a", "--asn"):
        current_isp = check_isp_with_retries()
        if current_isp is None:
            logger.error("Unable to determine current ISP/ASN. Exiting.")
            exit(1)
        if is_target_asn(current_isp=current_isp, target_asn=argv[2]):
            logger.info("Already connected to the target ASN. No reconnection needed.")
            exit(0)

    vendor = get_vendor_api()
    if vendor is None:
        logger.error("Unable to determine router vendor. Exiting.")
        exit(1)
    router = vendor()
    reconnection = Reconnection(router)
    reconnection.main()


if __name__ == "__main__":
    main()
