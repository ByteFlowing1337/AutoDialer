import importlib
import unittest
from typing import Any
from unittest.mock import Mock, patch

import requests

from autodialer.apis.utils.get_ip_address import get_ip_address

get_ip_address_module = importlib.import_module("autodialer.apis.utils.get_ip_address")


class TestGetIpAddress(unittest.TestCase):
    @patch.object(get_ip_address_module.requests, "get")
    def test_success_returns_sanitized_ip(self, mock_get: Any):
        response = Mock()
        response.raise_for_status.return_value = None
        response.text = " 203.0.113.10 \n"
        mock_get.return_value = response

        result = get_ip_address()

        self.assertEqual(result, "203.0.113.10")
        mock_get.assert_called_once_with(
            "https://api.ipify.org",
            proxies={"http": "", "https": ""},
            timeout=5,
        )

    @patch.object(
        get_ip_address_module.requests,
        "get",
        side_effect=requests.RequestException("Network error"),
    )
    def test_request_exception_returns_none(self, _mock_get: Any):
        result = get_ip_address()

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
