import importlib
import unittest
from typing import Any
from unittest.mock import Mock, patch

from autodialer.reconnection import ReconnectionError

reconnection_module = importlib.import_module("autodialer.reconnection")


class TestReconnection(unittest.TestCase):
    @staticmethod
    def _make_router(proto: str = "dhcp", reconnect_result: bool = True) -> Mock:
        router = Mock()
        router.get_wan_proto.return_value = proto
        router.dhcp_renew.return_value = reconnect_result
        router.pppoe_restart.return_value = reconnect_result
        return router

    def test_router_api_restart_wan_dhcp(self):
        from autodialer.routers import RouterAPI

        class MockRouter(RouterAPI):
            SUPPORTED_VENDORS = ("Mock",)

            def get_wan_proto(self):
                return "dhcp"

            def pppoe_restart(self):
                return False

            def dhcp_renew(self):
                return True

            def get_connected_devices(self):
                return []

        router = MockRouter()
        self.assertTrue(router.restart_wan())

    def test_router_api_restart_wan_pppoe(self):
        from autodialer.routers import RouterAPI

        class MockRouter(RouterAPI):
            SUPPORTED_VENDORS = ("Mock",)

            def get_wan_proto(self):
                return "pppoe"

            def pppoe_restart(self):
                return True

            def dhcp_renew(self):
                return False

            def get_connected_devices(self):
                return []

        router = MockRouter()
        self.assertTrue(router.restart_wan())

    @patch("builtins.exit")
    @patch.object(reconnection_module, "is_target_asn")
    @patch.object(reconnection_module, "check_isp_with_retries")
    @patch.object(reconnection_module, "get_internet_connectivity")
    def test_asn_mode_sleeps_before_each_isp_check(
        self,
        mock_get_internet_connectivity: Any,
        mock_check_isp_with_retries: Any,
        mock_is_target_asn: Any,
        mock_exit: Any,
    ):
        router = self._make_router(proto="dhcp")
        reconnector = reconnection_module.Reconnector(router, delay=7)

        events: list[str] = []
        isp_values = iter(["AS111 Example ISP", "AS222 Target ISP"])

        def wait_side_effect(*args, **kwargs):
            events.append("sleep")
            return True

        def isp_side_effect() -> str:
            events.append("check_isp")
            return next(isp_values)

        def is_target_side_effect(
            *, current_isp: str, target_asn: str | None = None
        ) -> bool:
            events.append("is_target")
            return current_isp.startswith("AS222")

        mock_get_internet_connectivity.side_effect = wait_side_effect
        mock_check_isp_with_retries.side_effect = isp_side_effect
        mock_is_target_asn.side_effect = is_target_side_effect

        reconnector.run_reconnection(mode="asn", asn="AS222", max_attempts=1)

        self.assertEqual(router.restart_wan.call_count, 1)
        self.assertEqual(mock_get_internet_connectivity.call_count, 1)
        self.assertEqual(mock_check_isp_with_retries.call_count, 2)
        self.assertEqual(
            events,
            ["check_isp", "is_target", "sleep", "check_isp", "is_target"],
        )
        mock_exit.assert_not_called()

    @patch("sys.exit", side_effect=SystemExit(1))
    @patch.object(reconnection_module, "get_internet_connectivity", return_value=False)
    @patch.object(reconnection_module, "get_ip_address", return_value=None)
    def test_change_mode_exits_when_initial_ip_fetch_fails(
        self,
        mock_get_ip_address: Any,
        _mock_get_internet_connectivity: Any,
        mock_exit: Any,
    ):
        router = self._make_router()
        reconnector = reconnection_module.Reconnector(router)

        with self.assertRaises(ReconnectionError) as context:
            reconnector.run_reconnection(mode="change", max_attempts=5, asn=None)

        self.assertEqual(str(context.exception), "Unable to fetch current IP address.")
        mock_get_ip_address.assert_called_once_with()
        router.restart_wan.assert_not_called()
        mock_exit.assert_not_called()

    @patch("sys.exit")
    @patch.object(
        reconnection_module, "check_isp_with_retries", return_value="AS9999 Example ISP"
    )
    @patch.object(reconnection_module, "get_internet_connectivity", return_value=True)
    @patch.object(
        reconnection_module,
        "get_ip_address",
        side_effect=["203.0.113.10", "203.0.113.10", "198.51.100.25"],
    )
    @patch("logging.Logger.info")
    def test_change_mode_retries_until_ip_changes(
        self,
        mock_logger_info: Any,
        mock_get_ip_address: Any,
        _mock_get_internet_connectivity: Any,
        mock_check_isp_with_retries: Any,
        mock_exit: Any,
    ):
        router = self._make_router()
        reconnector = reconnection_module.Reconnector(router)

        reconnector.run_reconnection(mode="change", max_attempts=5, asn=None)

        self.assertEqual(router.restart_wan.call_count, 2)
        self.assertEqual(mock_get_ip_address.call_count, 3)
        mock_logger_info.assert_called_with(
            "Successfully changed IP: %s -> %s %s",
            "203.0.113.10",
            "198.51.100.25",
            "AS9999 Example ISP",
        )
        mock_check_isp_with_retries.assert_called_once_with()
        mock_exit.assert_not_called()

    @patch("sys.exit", side_effect=SystemExit(1))
    @patch.object(reconnection_module, "get_internet_connectivity", return_value=True)
    @patch.object(
        reconnection_module,
        "get_ip_address",
        side_effect=[
            "203.0.113.10",
            "203.0.113.10",
            "203.0.113.10",
            "203.0.113.10",
        ],
    )
    def test_change_mode_exits_after_exhausting_attempts(
        self,
        mock_get_ip_address: Any,
        _mock_get_internet_connectivity: Any,
        mock_exit: Any,
    ):
        router = self._make_router()
        reconnector = reconnection_module.Reconnector(router)

        with self.assertRaises(ReconnectionError) as context:
            reconnector.run_reconnection(mode="change", max_attempts=3, asn=None)

        self.assertEqual(
            str(context.exception), "Failed to change IP address after 3 attempts."
        )
        self.assertEqual(router.restart_wan.call_count, 3)
        self.assertEqual(mock_get_ip_address.call_count, 4)
        mock_exit.assert_not_called()

    @patch.object(reconnection_module, "get_router")
    @patch.object(
        reconnection_module,
        "check_isp_with_retries",
        return_value="AS9929 Example ISP",
    )
    def test_asn_mode_exits_early_when_already_on_target_asn(
        self,
        _mock_check_isp: Any,
        mock_get_router: Any,
    ):
        router = self._make_router()
        mock_get_router.return_value = router

        reconnection_module.reconnect(mode="asn", asn="AS9929")

        router.restart_wan.assert_not_called()

    @patch.object(reconnection_module, "get_router", return_value=None)
    def test_reconnect_exits_when_no_router(self, mock_get_router):
        with self.assertRaises(ReconnectionError) as context:
            reconnection_module.reconnect(mode="force")
        self.assertEqual(
            str(context.exception),
            "Unable to detect router vendor or no API available.",
        )
        mock_get_router.assert_called_once_with()

    @patch.object(reconnection_module, "get_router", return_value=None)
    def test_reconnect_reject_illegal_attempts(self, mock_get_router):
        with self.assertRaises(ReconnectionError) as context:
            reconnection_module.reconnect(mode="force", max_attempts=0)
        self.assertEqual(
            str(context.exception), "The value of attempts must be at least 1."
        )


if __name__ == "__main__":
    unittest.main()
