import importlib
import unittest
from unittest.mock import patch

get_devices_module = importlib.import_module("autodialer.get_devices")


class TestGetDevices(unittest.TestCase):
    @patch("sys.stdout.isatty", return_value=True)
    @patch("builtins.print")
    @patch.object(get_devices_module, "get_devices")
    def test_print_colorful_devices_table_on_tty(
        self, mock_get_devices, mock_print, mock_isatty
    ):
        devices = [
            {
                "hostname": "Device1",
                "ip": "192.168.1.100",
                "mac": "00:11:22:33:44:55",
                "type": "Wireless",
                "up_kbps": 1000,
                "down_kbps": 500,
                "is_current": True,
            },
        ]
        mock_get_devices.return_value = devices
        from autodialer.get_devices import print_devices_table

        print_devices_table()
        has_ansi = any(
            "\033" in str(arg) for call in mock_print.call_args_list for arg in call[0]
        )
        self.assertTrue(has_ansi)  # Check for ANSI color codes

    @patch("sys.stdout.isatty", return_value=False)
    @patch("builtins.print")
    @patch.object(get_devices_module, "get_devices")
    def test_print_devices_table_without_color_on_non_tty(
        self, mock_get_devices, mock_print, mock_isatty
    ):
        devices = [
            {
                "hostname": "Device1",
                "ip": "192.168.1.100",
                "mac": "00:11:22:33:44:55",
                "type": "Wireless",
                "up_kbps": 1000,
                "down_kbps": 500,
                "is_current": True,
            },
        ]
        mock_get_devices.return_value = devices
        from autodialer.get_devices import print_devices_table

        print_devices_table()
        has_ansi = any(
            "\033" in str(arg) for call in mock_print.call_args_list for arg in call[0]
        )
        self.assertFalse(has_ansi)  # Check that no ANSI color codes are present

    @patch("sys.stdout.isatty", return_value=True)
    @patch("builtins.print")
    @patch.object(get_devices_module, "get_devices", return_value=[])
    def test_print_devices_table_with_no_devices(
        self, mock_get_devices, mock_print, mock_isatty
    ):
        from autodialer.get_devices import print_devices_table

        print_devices_table()
        mock_print.assert_called_with("No connected devices found.")

    @patch.object(get_devices_module, "get_router", return_value=None)
    def test_get_devices_raises_runtime_error_when_router_none(self, mock_get_router):
        from autodialer.get_devices import get_devices

        with self.assertRaises(RuntimeError) as context:
            get_devices()
        self.assertIn(
            "Unable to detect router vendor or no API available.",
            str(context.exception),
        )

    @patch("sys.stdout.isatty", return_value=False)
    @patch("builtins.print")
    @patch.object(get_devices_module, "get_devices")
    def test_print_devices_table_alignment(
        self, mock_get_devices, mock_print, mock_isatty
    ):
        devices = [
            {
                "hostname": "Device1",
                "ip": "192.168.1.100",
                "mac": "00:11:22:33:44:55",
                "type": "Wireless",
                "up_kbps": 1000,
                "down_kbps": 500,
                "is_current": True,
            },
            {
                "hostname": "Device2",
                "ip": "192.168.1.101",
                "mac": "AA:BB:CC:DD:EE:FF",
                "type": "Wired",
                "up_kbps": 2000,
                "down_kbps": 1500,
                "is_current": False,
            },
        ]
        mock_get_devices.return_value = devices
        from autodialer.get_devices import print_devices_table

        print_devices_table()
        output_lines = [call[0][0] for call in mock_print.call_args_list if call[0]]
        output_lines = [line for line in output_lines if line.strip()]
        col_starts = []
        for line in output_lines:
            indices = []
            last = 0
            for part in line.split():
                idx = line.find(part, last)
                indices.append(idx)
                last = idx + len(part)
            col_starts.append(indices)
        for col in zip(*col_starts, strict=False):
            assert len(set(col)) == 1, f"Column not aligned: {col}"
