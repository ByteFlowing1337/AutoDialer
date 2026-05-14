import logging
import sys
import argparse
from typing import Literal
from autodialer.routers import RouterAPI, get_router
from autodialer.network import (
    check_isp_with_retries,
    get_ip_address,
    is_target_asn,
    normalize_asn,
    try_connect,
)
from autodialer.config import parse_and_save_env_flags


logger = logging.getLogger(__name__)


class Reconnection:
    def __init__(self, router: RouterAPI, delay: int = 10, max_attempts: int = 5):
        self.router = router
        self.max_attempts = max_attempts
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
            sys.exit(1)

        match mode:
            case "force":
                if not self._apply_reconnection(proto):
                    sys.exit(1)

                if not try_connect(self.delay, self.max_attempts):
                    logger.error(
                        "Internet did not recover after forced reconnection. Exiting."
                    )
                    sys.exit(1)

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
                    sys.exit(1)

                after_reconnection_ip: str | None = current_ip
                attempts = 0

                while (
                    current_ip == after_reconnection_ip
                ) and attempts < self.max_attempts:
                    if not self._apply_reconnection(proto):
                        sys.exit(1)

                    if not try_connect(self.delay, self.max_attempts):
                        logger.error(
                            "Internet did not recover after reconnection. Exiting.",
                        )
                        sys.exit(1)

                    if (after_reconnection_ip := get_ip_address()) is None:
                        logger.error(
                            "Unable to fetch IP address after reconnection. Exiting."
                        )
                        sys.exit(1)
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
                sys.exit(1)

            case "asn":
                for _ in range(self.max_attempts):
                    if not self._apply_reconnection(proto):
                        sys.exit(1)

                    if not try_connect(self.delay, self.max_attempts):
                        logger.error(
                            "Internet did not recover after reconnection. Exiting."
                        )
                        sys.exit(1)

                    isp = check_isp_with_retries()
                    if isp is None:
                        sys.exit(1)

                    if is_target_asn(current_isp=isp, target_asn=asn):
                        return

                logger.error(
                    "Reached maximum reconnection attempts without switching to the desired ASN."
                )
                sys.exit(1)

    def main(
        self, mode: Literal["force", "asn", "change"], asn: str | None = None
    ) -> None:
        match mode:
            case "force":
                self.run_reconnection(mode="force", asn=None)
            case "asn":
                self.run_reconnection(mode="asn", asn=asn)
            case "change":
                self.run_reconnection(mode="change", asn=None)


def validate_asn(value: str) -> str:
    normalized = normalize_asn(value)
    if not normalized:
        raise argparse.ArgumentTypeError(
            f"Invalid ASN format: '{value}'. Valid range is AS1 to AS4294967295."
        )
    return normalized


def reconnection():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(
        description="Restart router WAN connection to obtain a new IP address or switch ASNs."
    )
    parser.add_argument(
        "-e",
        "--env",
        metavar="<KEY=VAL>",
        action="append",
        help="Set environment variables (e.g., -e PANEL_PASSWORD=secret)",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force a reconnection regardless of current ASN.",
    )
    group.add_argument(
        "-a",
        "--asn",
        metavar="<ASN>",
        type=validate_asn,
        help="Reconnect until connected to the specified target ASN.",
    )
    group.add_argument(
        "-c",
        "--change",
        action="store_true",
        help="Reconnect until the public IP address changes.",
    )

    args = parser.parse_args()
    if args.env:
        parse_and_save_env_flags()

    router = get_router()
    if router is None:
        logger.error(
            "Unable to detect router vendor or no API implementation available. Exiting."
        )
        sys.exit(1)
    rec = Reconnection(router)
    if args.force:
        rec.main(mode="force")
    elif args.asn:
        rec.main(mode="asn", asn=normalize_asn(args.asn))
    elif args.change:
        rec.main(mode="change")


if __name__ == "__main__":
    reconnection()
