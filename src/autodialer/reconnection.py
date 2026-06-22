import logging
from typing import Literal

from autodialer.network import (
    check_isp_with_retries,
    get_internet_connectivity,
    get_ip_address,
    get_router,
)
from autodialer.routers import RouterAPI
from autodialer.utils import is_target_asn

logger = logging.getLogger(__name__)

DEFAULT_MAX_ATTEMPTS = 5


class ReconnectionError(RuntimeError):
    """Custom exception for reconnection-related errors."""


class Reconnector:
    def __init__(self, router: RouterAPI, delay: int = 10) -> None:
        self.router = router
        self.delay = delay

    def run_reconnection(
        self,
        mode: Literal["force", "asn", "change"],
        *,
        asn: str | None,
        max_attempts: int,
    ) -> None:
        if mode == "force":
            return self._reconnect_forcefully(max_attempts)
        elif mode == "change":
            return self._reconnect_util_change_ip(max_attempts)
        elif mode == "asn":
            if not self._validate_asn(asn):
                return
            return self._reconnect_util_target_asn(
                target_asn=asn,  # type: ignore
                max_attempts=max_attempts,
            )
        else:
            raise ReconnectionError(f"Invalid reconnection mode: {mode}")

    def _reconnect_forcefully(self, max_attempts: int) -> None:
        if not self.router.restart_wan():
            raise ReconnectionError("Failed to apply forced reconnection.")

        if not get_internet_connectivity(self.delay, max_attempts):
            raise ReconnectionError(
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

    def _reconnect_util_change_ip(self, max_attempts: int) -> None:
        if (current_ip := get_ip_address()) is None:
            raise ReconnectionError("Unable to fetch current IP address.")

        after_reconnection_ip: str | None = current_ip
        attempts = 0

        while (current_ip == after_reconnection_ip) and attempts < max_attempts:
            if not self.router.restart_wan():
                raise ReconnectionError("Failed to apply reconnection.")

            if not get_internet_connectivity(self.delay, max_attempts):
                raise ReconnectionError(
                    "Cannot detect internet connectivity after reconnection."
                )

            if (after_reconnection_ip := get_ip_address()) is None:
                raise ReconnectionError(
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
        raise ReconnectionError(
            f"Failed to change IP address after {max_attempts} attempts."
        )

    def _reconnect_util_target_asn(self, target_asn: str, max_attempts: int) -> None:
        for _ in range(max_attempts):
            if not self.router.restart_wan():
                raise ReconnectionError("Failed to apply reconnection.")

            if not get_internet_connectivity(self.delay, max_attempts):
                raise ReconnectionError(
                    "Cannot detect internet connectivity after reconnection."
                )

            isp = check_isp_with_retries()
            if isp is None:
                raise ReconnectionError("Unable to fetch ISP information.")

            if is_target_asn(current_isp=isp, target_asn=target_asn):
                return

        raise ReconnectionError(
            "Reached maximum reconnection attempts without "
            "switching to the desired ASN."
        )

    def _validate_asn(self, asn: str | None) -> bool:
        if asn is None:
            raise ReconnectionError("Target ASN must be provided for ASN mode.")
        current_isp = check_isp_with_retries()
        if current_isp is None:
            raise ReconnectionError("Unable to fetch ISP information.")
        if is_target_asn(current_isp=current_isp, target_asn=asn):
            logger.info(
                "Already connected to target ASN %s. No reconnection needed.",
                asn,
            )
            return False
        return True


def reconnect(
    *,
    mode: Literal["force", "asn", "change"],
    asn: str | None = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> None:

    router = get_router()
    if router is None:
        raise ReconnectionError("Unable to detect router vendor or no API available.")
    reconnector = Reconnector(router)
    reconnector.run_reconnection(mode=mode, max_attempts=max_attempts, asn=asn)
