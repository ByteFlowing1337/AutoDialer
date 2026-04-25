import importlib
import unittest
from typing import Any
from unittest.mock import Mock, patch


reconnection_module = importlib.import_module("autodialer.reconnection")


class TestParseArguments(unittest.TestCase):
    @patch.object(reconnection_module, "is_target_asn", return_value=True)
    @patch.object(
        reconnection_module,
        "check_isp_with_retries",
        return_value="AS9929 Example ISP",
    )
    @patch("builtins.exit", side_effect=SystemExit(0))
    def test_asn_mode_exits_early_when_already_on_target_asn(
        self,
        _mock_exit: Any,
        _mock_check_isp: Any,
        _mock_is_target_asn: Any,
    ):
        with patch.object(
            reconnection_module, "argv", ["autodialer", "--asn", "AS9929"]
        ):
            with self.assertRaises(SystemExit) as context:
                reconnection_module.parse_arguments("AS9929")

        self.assertEqual(context.exception.code, 0)


class TestReconnection(unittest.TestCase):
    @staticmethod
    def _make_router(proto: str = "dhcp", reconnect_result: bool = True) -> Mock:
        router = Mock()
        router.get_wan_proto.return_value = proto
        router.dhcp_renew.return_value = reconnect_result
        router.make_pppoe_reconnection.return_value = reconnect_result
        return router

    def test_get_wan_proto_uses_router_contract(self):
        router = Mock()
        router.get_wan_proto.return_value = "dhcp"

        reconnection = reconnection_module.Reconnection(router)

        self.assertEqual(reconnection._get_wan_proto(), "dhcp")

    @patch("autodialer.network.wait_internet_recovery.sleep")
    def test_apply_reconnection_calls_pppoe_method(self, mock_sleep: Any):
        router = Mock()
        router.make_pppoe_reconnection.return_value = True

        reconnection = reconnection_module.Reconnection(router)

        self.assertTrue(reconnection._apply_reconnection("pppoe"))
        router.make_pppoe_reconnection.assert_called_once_with()

    @patch("builtins.exit")
    @patch.object(reconnection_module, "is_target_asn")
    @patch.object(reconnection_module, "check_isp_with_retries")
    @patch.object(reconnection_module, "wait_internet_recovery")
    def test_asn_mode_sleeps_before_each_isp_check(
        self,
        mock_wait_internet_recovery: Any,
        mock_check_isp_with_retries: Any,
        mock_is_target_asn: Any,
        mock_exit: Any,
    ):
        router = self._make_router(proto="dhcp")
        reconnection = reconnection_module.Reconnection(router, delay=7, max_attempts=3)

        events: list[str] = []
        isp_values = iter(["AS111 Example ISP", "AS222 Target ISP"])

        def wait_side_effect() -> None:
            events.append("sleep")

        def isp_side_effect() -> str:
            events.append("check_isp")
            return next(isp_values)

        def is_target_side_effect(isp: str, asn: str | None = None) -> bool:
            events.append("is_target")
            return isp.startswith("AS222")

        mock_wait_internet_recovery.side_effect = wait_side_effect
        mock_check_isp_with_retries.side_effect = isp_side_effect
        mock_is_target_asn.side_effect = is_target_side_effect

        reconnection.run_reconnection(mode="asn", asn="AS222")

        self.assertEqual(router.dhcp_renew.call_count, 2)
        self.assertEqual(mock_wait_internet_recovery.call_count, 2)
        self.assertEqual(mock_check_isp_with_retries.call_count, 2)
        self.assertEqual(
            events,
            ["sleep", "check_isp", "is_target", "sleep", "check_isp", "is_target"],
        )
        mock_exit.assert_not_called()

    @patch("builtins.exit", side_effect=SystemExit(1))
    @patch("autodialer.network.wait_internet_recovery.sleep")
    @patch.object(reconnection_module, "get_ip_address", return_value=None)
    def test_change_mode_exits_when_initial_ip_fetch_fails(
        self, mock_get_ip_address: Any, mock_sleep: Any, mock_exit: Any
    ):
        router = self._make_router()
        reconnection = reconnection_module.Reconnection(router)

        with self.assertRaises(SystemExit) as context:
            reconnection.run_reconnection(mode="change", asn=None)

        self.assertEqual(context.exception.code, 1)
        mock_get_ip_address.assert_called_once_with()
        router.dhcp_renew.assert_not_called()
        mock_exit.assert_called_once_with(1)

    @patch("builtins.exit")
    @patch("autodialer.network.wait_internet_recovery.sleep")
    @patch.object(
        reconnection_module,
        "get_ip_address",
        side_effect=["203.0.113.10", "203.0.113.10", "198.51.100.25"],
    )
    def test_change_mode_retries_until_ip_changes(
        self,
        mock_get_ip_address: Any,
        mock_sleep: Any,
        mock_exit: Any,
    ):
        router = self._make_router()
        reconnection = reconnection_module.Reconnection(router)

        reconnection.run_reconnection(mode="change", asn=None)

        self.assertEqual(router.dhcp_renew.call_count, 2)
        self.assertEqual(mock_get_ip_address.call_count, 3)
        mock_exit.assert_not_called()

    @patch("builtins.exit", side_effect=SystemExit(1))
    @patch("autodialer.network.wait_internet_recovery.sleep")
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
        self, mock_get_ip_address: Any, mock_sleep: Any, mock_exit: Any
    ):
        router = self._make_router()
        reconnection = reconnection_module.Reconnection(router)
        reconnection.max_attempts = 3

        with self.assertRaises(SystemExit) as context:
            reconnection.run_reconnection(mode="change", asn=None)

        self.assertEqual(context.exception.code, 1)
        self.assertEqual(router.dhcp_renew.call_count, 3)
        self.assertEqual(mock_get_ip_address.call_count, 4)
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
