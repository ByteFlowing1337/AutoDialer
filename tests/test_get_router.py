import importlib
import unittest
from unittest.mock import patch
from typing import Any

get_router_module = importlib.import_module("autodialer.routers.get_router")
AsusAPI = importlib.import_module("autodialer.routers.asus.asus_api").AsusAPI


class TestGetRouter(unittest.TestCase):
    @patch.object(AsusAPI, "__init__", return_value=None)
    @patch.object(get_router_module, "check_router_vendor", return_value="ASUS")
    def test_get_router_returns_router_api_instance(
        self, mock_check_vendor: Any, mock_asus_init: Any
    ):
        router = get_router_module.get_router()

        self.assertIsInstance(router, AsusAPI)

        self.assertTrue(hasattr(router, "get_wan_proto"))
        self.assertTrue(hasattr(router, "dhcp_renew"))
        self.assertTrue(hasattr(router, "make_pppoe_reconnection"))
        self.assertTrue(hasattr(router, "get_connected_devices"))

    @patch.object(get_router_module, "check_router_vendor", return_value=None)
    def test_get_router_returns_none_when_vendor_not_detected(
        self, mock_check_vendor: Any
    ):
        router = get_router_module.get_router()
        self.assertIsNone(router)

    @patch.object(get_router_module, "check_router_vendor", return_value="Unknown")
    def test_get_router_returns_none_for_unknown_vendor(self, mock_check_vendor: Any):
        router = get_router_module.get_router()
        self.assertIsNone(router)
