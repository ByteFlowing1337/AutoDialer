import importlib
import unittest
from typing import Any
from unittest.mock import patch


vendor_api_module = importlib.import_module("autodialer.apis.utils.get_vendor_api")


class TestGetVendorApi(unittest.TestCase):
    @patch.object(vendor_api_module, "check_router_vendor", return_value="ASUS")
    def test_returns_asus_api_for_asus_vendor(self, _mock_vendor: Any):
        api_class = vendor_api_module.get_vendor_api()

        self.assertIsNotNone(api_class)
        self.assertEqual(api_class.__name__, "AsusAPI")
