import logging
from functools import lru_cache
from importlib import import_module

from autodialer.network.check_vendor import check_router_vendor
from autodialer.routers.base_router_api import RouterAPI

logger = logging.getLogger(__name__)

VENDOR_API_MAP: dict[str, tuple[str, str]] = {
    "asus": ("autodialer.routers.asus.asus_api", "AsusAPI"),
    "asus aimesh": ("autodialer.routers.asus.asus_api", "AsusAPI"),
    "tp-link": ("autodialer.routers.tplink.tplink_api", "TPLinkAPI"),
    "zte": ("autodialer.routers.zte.zte_api", "ZTEApi"),
}


@lru_cache(maxsize=1)
def _get_vendor_api_registry(vendor: str) -> type[RouterAPI] | None:
    mapping = VENDOR_API_MAP.get(vendor.casefold())
    if mapping is None:
        return None

    module_name, class_name = mapping
    module = import_module(module_name)
    api_class = getattr(module, class_name, None)

    if api_class is None:
        return None

    return api_class if issubclass(api_class, RouterAPI) else None


def _get_vendor_api() -> type[RouterAPI] | None:
    """
    Get the vendor-specific router API class.

    Returns:
        type[RouterAPI] | None: A concrete implementation of the router API
        (for example, ``AsusAPI``), or ``None`` if the router vendor cannot
        be detected or no API implementation is registered for that vendor.

    Example:
    ```
    api_class = _get_vendor_api()
    if api_class is not None:
        router = api_class()
    ```
    """
    vendor = check_router_vendor()
    if vendor is None:
        return None

    api_class = _get_vendor_api_registry(vendor.casefold())
    if api_class is None:
        logger.error("No API implementation for vendor: %s", vendor)

    return api_class


def get_router() -> RouterAPI | None:
    api_class = _get_vendor_api()
    if api_class is not None:
        return api_class()
    return None
