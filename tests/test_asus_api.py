import importlib
import unittest
from typing import Any
from unittest.mock import Mock, call, patch


asus_module = importlib.import_module("autodialer.apis.routers.asus.asus_api")
AsusAPI = asus_module.AsusAPI


class TestAsusAPI(unittest.TestCase):
    @patch.object(asus_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(asus_module, "PANEL_USERNAME", "admin")
    @patch.object(asus_module, "get_gateway_ip", return_value="192.168.50.1")
    @patch.object(asus_module.requests, "Session")
    def test_get_wan_proto_uses_active_wan_unit(
        self,
        mock_session_cls: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()

        login_response = Mock()
        login_response.raise_for_status.return_value = None
        login_response.json.return_value = {"asus_token": "test-token"}

        status_response = Mock()
        status_response.raise_for_status.return_value = None
        status_response.json.return_value = {
            "get_wan_unit": 1,
            "wan0_proto": "pppoe",
            "wan1_proto": "dhcp",
        }

        session.post.side_effect = [login_response, status_response]
        mock_session_cls.return_value = session

        router = AsusAPI()

        self.assertEqual(router.get_wan_proto(), "dhcp")

    @patch.object(asus_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(asus_module, "PANEL_USERNAME", "admin")
    @patch.object(asus_module, "get_gateway_ip", return_value="192.168.50.1")
    @patch.object(asus_module.requests, "Session")
    def test_dhcp_renew_falls_back_to_restart_wan(
        self,
        mock_session_cls: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()

        login_response = Mock()
        login_response.raise_for_status.return_value = None
        login_response.json.return_value = {"asus_token": "test-token"}

        session.post.return_value = login_response
        mock_session_cls.return_value = session

        router = AsusAPI()

        with (
            patch.object(
                router,
                "get_wan_status",
                return_value={"get_wan_unit": 1},
            ),
            patch.object(router, "_run_service", side_effect=[False, True]) as mock_run,
        ):
            self.assertTrue(router.dhcp_renew())

        self.assertEqual(
            mock_run.call_args_list,
            [call("restart_wan1"), call("restart_wan")],
        )
