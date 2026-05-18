from abc import ABC, abstractmethod
from typing import ClassVar


class RouterAPI(ABC):
    SUPPORTED_VENDORS: ClassVar[tuple[str, ...]]

    def __init__(self):
        if type(self) is RouterAPI:
            raise TypeError("Cannot instantiate abstract class")

    @abstractmethod
    def get_wan_proto(self) -> str | None: ...

    @abstractmethod
    def make_pppoe_reconnection(self) -> bool: ...

    @abstractmethod
    def dhcp_renew(self) -> bool: ...

    @abstractmethod
    def get_connected_devices(self) -> list: ...
