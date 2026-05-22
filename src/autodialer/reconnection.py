import logging
from typing import Literal

from autodialer.network import (
    check_isp_with_retries,
    get_internet_connectivity,
    get_ip_address,
    get_router,
    is_target_asn,
)
from autodialer.routers import RouterAPI

logger = logging.getLogger(__name__)


class Reconnection:
    DEFAULT_MAX_ATTEMPTS = 5

    def __init__(self, router: RouterAPI, delay: int = 10):
        self.router = router
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
        self,
        mode: Literal["force", "asn", "change"],
        *,
        asn: str | None,
        attempts: int | None = None,
    ) -> None:
        self.max_attempts = attempts if attempts is not None else self.DEFAULT_MAX_ATTEMPTS
        proto = self._get_wan_proto()

        if proto is None:
            raise RuntimeError("Unable to determine current WAN protocol.")

        match mode:
            case "force":
                if not self._apply_reconnection(proto):
                    raise RuntimeError("Failed to apply forced reconnection.")

                if not get_internet_connectivity(self.delay, self.max_attempts):
                    raise RuntimeError(
                        "Cannot detect internet connectivity after forced reconnection."
                    )

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
                    raise RuntimeError("Unable to fetch current IP address.")

                after_reconnection_ip: str | None = current_ip
                attempts = 0

                while (
                    current_ip == after_reconnection_ip
                ) and attempts < self.max_attempts:
                    if not self._apply_reconnection(proto):
                        raise RuntimeError("Failed to apply reconnection.")

                    if not get_internet_connectivity(self.delay, self.max_attempts):
                        raise RuntimeError(
                            "Cannot detect internet connectivity after reconnection."
                        )

                    if (after_reconnection_ip := get_ip_address()) is None:
                        raise RuntimeError(
                            "Unable to fetch IP address after reconnection."
                        )
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
                raise RuntimeError(
                    f"Failed to change IP address after {self.max_attempts} attempts."
                )

            case "asn":
                for _ in range(self.max_attempts):
                    if not self._apply_reconnection(proto):
                        raise RuntimeError("Failed to apply reconnection.")

                    if not get_internet_connectivity(self.delay, self.max_attempts):
                        raise RuntimeError(
                            "Cannot detect internet connectivity after reconnection."
                        )

                    isp = check_isp_with_retries()
                    if isp is None:
                        raise RuntimeError("Unable to fetch ISP information.")

                    if is_target_asn(current_isp=isp, target_asn=asn):
                        return

                raise RuntimeError(
                    "Reached maximum reconnection attempts without "
                    "switching to the desired ASN."
                )

    def main(
        self,
        mode: Literal["force", "asn", "change"],
        asn: str | None = None,
        attempts: int | None = None,
    ) -> None:
        match mode:
            case "force":
                self.run_reconnection(mode="force", asn=None, attempts=attempts)
            case "asn":
                self.run_reconnection(mode="asn", asn=asn, attempts=attempts)
            case "change":
                self.run_reconnection(mode="change", asn=None, attempts=attempts)


def reconnect(
    *,
    mode: Literal["force", "asn", "change"],
    asn: str | None = None,
    attempts: int | None = None,
) -> None:

    router = get_router()
    if router is None:
        raise RuntimeError("Unable to detect router vendor or no API available.")
    reconnection = Reconnection(router)
    reconnection.main(mode, asn, attempts)
