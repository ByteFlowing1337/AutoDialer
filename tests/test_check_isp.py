import importlib
import unittest
from typing import Any
from unittest.mock import Mock, patch

import requests

from autodialer import check_isp, check_isp_with_retries

check_isp_module = importlib.import_module("autodialer.network.check_isp")


class TestCheckIsp(unittest.TestCase):
    @patch.object(check_isp_module.requests, "get")
    def test_check_isp_success_returns_org(self, mock_get: Any):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"org": "AS1234 Example ISP"}
        mock_get.return_value = response

        result = check_isp()

        self.assertEqual(result, "AS1234 Example ISP")

    @patch.object(check_isp_module.requests, "get", side_effect=requests.Timeout)
    def test_check_isp_timeout_returns_none(self, _mock_get: Any):
        result = check_isp()
        self.assertIsNone(result)

    @patch.object(check_isp_module.requests, "get")
    def test_check_isp_invalid_payload_returns_none(self, mock_get: Any):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"unexpected": "value"}
        mock_get.return_value = response

        result = check_isp()

        self.assertIsNone(result)


class TestCheckIspWithRetries(unittest.TestCase):
    @patch.object(
        check_isp_module, "check_isp", side_effect=[None, None, "AS9999 Retry ISP"]
    )
    def test_retries_until_success(self, mock_check_isp: Any):
        result = check_isp_with_retries(retries=3)

        self.assertEqual(result, "AS9999 Retry ISP")

    @patch.object(check_isp_module, "check_isp", return_value=None)
    def test_returns_none_after_all_retries(self, mock_check_isp: Any):
        result = check_isp_with_retries(retries=2)

        self.assertIsNone(result)

    @patch.object(check_isp_module, "check_isp")
    def test_invalid_retry_parameters_return_none(self, mock_check_isp: Any):
        self.assertIsNone(check_isp_with_retries(retries=-1))
        self.assertIsNone(check_isp_with_retries(retries=0))
        mock_check_isp.assert_not_called()


if __name__ == "__main__":
    unittest.main()
