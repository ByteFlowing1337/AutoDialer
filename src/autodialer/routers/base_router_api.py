from abc import ABC, abstractmethod
from typing import ClassVar


class AbstractRouterAPI(ABC):
    SUPPORTED_VENDORS: ClassVar[tuple[str, ...]]

    @abstractmethod
    def get_wan_proto(self) -> str | None: ...

    @abstractmethod
    def pppoe_restart(self) -> bool: ...

    @abstractmethod
    def dhcp_renew(self) -> bool: ...

    @abstractmethod
    def restart_wan(self) -> bool: ...

    @abstractmethod
    def get_connected_devices(self) -> list: ...


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
