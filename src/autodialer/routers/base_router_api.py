from abc import ABC, abstractmethod
from typing import ClassVar


class AbstractRouterAPI(ABC):
    SUPPORTED_VENDORS: ClassVar[tuple[str, ...]]

    @abstractmethod
    def get_wan_proto(self) -> str | None:
        """Return the lower case of WLAN protocol, i.e. (pppoe,dhcp)."""

    @abstractmethod
    def pppoe_restart(self) -> bool:
        """Restart the router by PPPoE protocol."""

    @abstractmethod
    def dhcp_renew(self) -> bool:
        """Restart the router by DHCP protocol."""

    @abstractmethod
    def restart_wan(self) -> bool:
        """Restart the router."""

    @abstractmethod
    def get_connected_devices(self) -> list:
        """Get the information of connected devices."""


class RouterAPI(AbstractRouterAPI):
    def restart_wan(self) -> bool:
        proto = self.get_wan_proto()
        if proto is None:
            return False
        elif proto == "dhcp":
            return self.dhcp_renew()
        elif proto == "pppoe":
            return self.pppoe_restart()
        return False
