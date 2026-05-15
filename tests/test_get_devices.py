import unittest
from unittest.mock import patch


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
        with patch("sys.stdout.isatty", return_value=True):
            with patch("builtins.print") as mock_print:
                from autodialer.get_devices import print_devices_table

                print_devices_table(devices)
                self.assertIn(
                    "\033", mock_print.call_args[0][0]
                )  # Check for ANSI color codes

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
        with patch("sys.stdout.isatty", return_value=False):
            with patch("builtins.print") as mock_print:
                from autodialer.get_devices import print_devices_table

                print_devices_table(devices)
                self.assertNotIn(
                    "\033", mock_print.call_args[0][0]
                )  # Check that no ANSI color codes are present
