__version__ = "0.4.0"
__author__ = "Byteflow"


def __getattr__(name):
    if name == "get_devices":
        from .get_devices import get_devices

        return get_devices
    elif name == "print_devices_table":
        from .get_devices import print_devices_table

        return print_devices_table
    elif name == "reconnect":
        from .reconnection import reconnect

        return reconnect
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = [
    "get_devices",
    "print_devices_table",
    "reconnect",
]
