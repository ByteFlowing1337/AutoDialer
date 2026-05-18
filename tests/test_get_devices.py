import importlib
import unittest
from unittest.mock import patch

get_devices_module = importlib.import_module("autodialer.get_devices")


class TestGetDevices(unittest.TestCase):
    def test_print_colorful_devices_table_on_tty(self):
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
        from autodialer.get_devices import print_devices_table

        with (
            patch("sys.stdout.isatty", return_value=True),
            patch("builtins.print") as mock_print,
            patch.object(get_devices_module, "get_devices", return_value=devices),
        ):
            print_devices_table()
            has_ansi = any(
                "\033" in str(arg)
                for call in mock_print.call_args_list
                for arg in call[0]
            )
            self.assertTrue(has_ansi)  # Check for ANSI color codes

    def test_print_devices_table_without_color_on_non_tty(self):
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
        from autodialer.get_devices import print_devices_table

        with (
            patch("sys.stdout.isatty", return_value=False),
            patch("builtins.print") as mock_print,
            patch.object(get_devices_module, "get_devices", return_value=devices),
        ):
            print_devices_table()
            has_ansi = any(
                "\033" in str(arg)
                for call in mock_print.call_args_list
                for arg in call[0]
            )
            self.assertFalse(has_ansi)  # Check that no ANSI color codes are present
