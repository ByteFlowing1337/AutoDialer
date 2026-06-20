import logging
from typing import Literal
from urllib.parse import unquote

import requests

from autodialer.config import load_env_file
from autodialer.network.get_gateway import format_ip_for_url_host, get_gateway_ip
from autodialer.routers.base_router_api import RouterAPI
from autodialer.routers.tplink.tplink_security_encode import tplink_security_encode

env_var = load_env_file()
PANEL_PASSWORD: str = env_var.PANEL_PASSWORD
PPPOE_USERNAME: str | None = env_var.PPPOE_USERNAME
PPPOE_PASSWORD: str | None = env_var.PPPOE_PASSWORD

logger = logging.getLogger(__name__)


class TPLinkAPI(RouterAPI):
    """A class to interact with TP-Link routers using their API.

    Attributes:

        router_ip: The IP address of the router, obtained from the default gateway,
        using get_gateway_ip().

        password: The **encoded** password for logging into the router.

        username: The PPPoE username for authentication.

        pppoe_password: The PPPoE password for authentication.

        stok: The session token obtained after logging into the router,
              used for authenticated requests.
    """

    SUPPORTED_VENDORS = ("TP-Link",)

    router_ip: str | None
    password: str | None
    username: str | None
    pppoe_password: str | None
    stok: str | None

    def __init__(self):
        self.router_ip = None
        self.session = requests.Session()
        self.password = tplink_security_encode(PANEL_PASSWORD)
        self.username = PPPOE_USERNAME or None
        self.pppoe_password = PPPOE_PASSWORD or None
        self.stok = None

    def __post(self, *, path: str = "", payload: dict) -> dict:
        self.router_ip = self.router_ip or get_gateway_ip()
        router_host = format_ip_for_url_host(self.router_ip)
        url = f"http://{router_host}{path}"
        response = self.session.post(url, json=payload)
        return response.json()

    def __post_with_auth(self, *, payload: dict) -> dict:
        if not self.stok:
            self.stok = self.__login_router()
        if not self.stok:
            logger.error(
                "Cannot authenticate with the router. No session token obtained."
            )
            return {}
        return self.__post(path=f"/stok={self.stok}/ds", payload=payload)

    def __login_router(self) -> str | None:
        payload = {"method": "do", "login": {"password": self.password}}
        response = self.__post(payload=payload)
        stok = response.get("stok")
        if response.get("error_code") != 0 or response.get("stok") is None:
            logger.error("Login failed.")
            logger.debug(response)
            import sys

            sys.exit(1)
        return stok if isinstance(stok, str) else None

    def _set_credentials(self) -> bool:
        if not self.username or not self.pppoe_password:
            logger.warning(
                "Missing PPPoE credentials override. "
                "Will reuse the credentials already saved on the router."
            )
            return False

        payload = {
            "protocol": {
                "wan": {"wan_type": "pppoe"},
                "pppoe": {"username": self.username, "password": self.pppoe_password},
            },
            "method": "set",
        }

        response = self.__post_with_auth(payload=payload)
        if response.get("error_code") != 0:
            logger.error("Failed to set PPPoE credentials.")
            logger.debug(response)
            return False
        return True

    def _tplink_change_wan_status_request(
        self, action: Literal["connect", "disconnect", "renew"], method: str, proto: str
    ) -> bool:
        payload = {
            "network": {"change_wan_status": {"proto": proto, "operate": action}},
            "method": method,
        }
        response = self.__post_with_auth(payload=payload)
        if response.get("error_code") != 0:
            logger.error("Failed to %s %s.", action, proto)
            logger.debug(response)
            return False
        return True

    def _tplink_get_wan_status(self) -> dict:
        payload = {
            "network": {"name": ["wan_status", "wanv6_status"]},
            "protocol": {"name": ["dhcp", "ipv6_info"]},
            "method": "get",
        }
        response = self.__post_with_auth(payload=payload)
        if response.get("error_code") != 0:
            logger.error("Failed to get WAN status.")
            logger.debug(response)
            return {}
        return response

    def get_wan_proto(self) -> str | None:
        status = self._tplink_get_wan_status()
        wan_status = status.get("network", {}).get("wan_status", {})
        proto = wan_status.get("proto")
        return proto if isinstance(proto, str) else None

    def pppoe_restart(self) -> bool:

        if self.username and self.pppoe_password and not self._set_credentials():
            return False

        if not self._tplink_change_wan_status_request(
            action="disconnect", method="do", proto="pppoe"
        ):
            return False

        return self._tplink_change_wan_status_request(
            action="connect", method="do", proto="pppoe"
        )

    def dhcp_renew(self) -> bool:
        return self._tplink_change_wan_status_request(
            action="renew", method="do", proto="dhcp"
        )

    def get_connected_devices(self) -> list:
        payload = {
            "hosts_info": {"table": "host_info", "name": "cap_host_num"},
            "network": {"name": "iface_mac"},
            "hyfi": {"table": ["connected_ext"]},
            "method": "get",
        }
        response = self.__post_with_auth(payload=payload)
        if response.get("error_code") != 0:
            logger.error("Failed to get connected devices.")
            logger.debug(response)
            return []

        raw_hosts = response.get("hosts_info", {}).get("host_info", [])
        devices: list[dict] = []

        for item in raw_hosts:
            host: dict[str, str] = next(
                iter(item.values()), {}
            )  # host_info_0 / host_info_1 -> {...}
            devices.append(
                {
                    "hostname": unquote(host.get("hostname", "")) or "(unknown)",
                    "ip": host.get("ip", "-"),
                    "mac": host.get("mac", "-"),
                    "type": "wireless" if host.get("type") == "1" else "wired",
                    "is_current": host.get("is_cur_host") == "1",
                    "up_kbps": int(host.get("up_speed", "0")),
                    "down_kbps": int(host.get("down_speed", "0")),
                }
            )
        return devices
