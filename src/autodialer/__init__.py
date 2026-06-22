__version__ = "0.4.0"
__author__ = "Byteflow"

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from autodialer.get_devices import get_devices, print_devices_table
    from autodialer.network import get_router
    from autodialer.reconnection import reconnect
    from autodialer.routers import RouterAPI

__all__ = ["get_devices", "print_devices_table", "reconnect", "RouterAPI", "get_router"]


def __getattr__(name):
    if name == "get_devices":
        from autodialer.get_devices import get_devices

        return get_devices
    elif name == "print_devices_table":
        from autodialer.get_devices import print_devices_table

        return print_devices_table
    elif name == "reconnect":
        from autodialer.reconnection import reconnect

        return reconnect
    elif name == "RouterAPI":
        from autodialer.routers import RouterAPI

        return RouterAPI
    elif name == "get_router":
        from autodialer.network import get_router

        return get_router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
