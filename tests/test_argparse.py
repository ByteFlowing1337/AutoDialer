import importlib
import unittest
from unittest.mock import patch

cli_module = importlib.import_module("autodialer.cli")


class TestArgParse(unittest.TestCase):
    @patch("sys.argv", ["autodialer", "--help"])
    def test_help_mode_exits_with_zero(self):
        with self.assertRaises(SystemExit) as context:
            cli_module.main()
        self.assertEqual(context.exception.code, 0)

    @patch("sys.argv", ["autodialer", "-f", "--invalid"])
    def test_invalid_argument_exits_with_error(self):
        with patch("sys.stderr.write") as mock_stderr:
            with self.assertRaises(SystemExit) as context:
                cli_module.main()
            self.assertEqual(context.exception.code, 2)
            self.assertTrue(
                any(
                    "unrecognized arguments" in call[0][0]
                    for call in mock_stderr.call_args_list
                )
            )

    @patch("sys.argv", ["autodialer", "--asn"])
    def test_asn_argument_without_value_exits_with_error(self):
        with patch("sys.stderr.write") as mock_stderr:
            with self.assertRaises(SystemExit) as context:
                cli_module.main()
            self.assertEqual(context.exception.code, 2)
            self.assertTrue(
                any(
                    "expected one argument" in call[0][0]
                    for call in mock_stderr.call_args_list
                )
            )

    @patch("sys.argv", ["autodialer", "--force"])
    @patch("autodialer.reconnection.get_router", return_value=None)
    @patch("autodialer.reconnection.logger")
    def test_force_mode_without_router_exits_with_error(
        self, mock_logger, mock_get_router
    ):
        with self.assertRaises(RuntimeError) as context:
            cli_module.main()
        self.assertEqual(
            str(context.exception),
            "Unable to detect router vendor or no API available.",
        )
        mock_get_router.assert_called_once_with()

    def test_asn_mode_with_invalid_asn_value_exits_with_error(self):
        invalid_asns = [
            "-1",
            "f",
            "9999999999999999999",
            "AS0",
            "AS-123",
            "ASABC",
            "trash",
        ]

        for invalid_asn in invalid_asns:
            with (
                self.subTest(asn=invalid_asn),
                patch("sys.argv", ["autodialer", "--asn", invalid_asn]),
                patch("sys.stderr.write") as mock_stderr,
                self.assertRaises(SystemExit) as context,
            ):
                cli_module.main()
            self.assertEqual(context.exception.code, 2)
            self.assertTrue(
                any(
                    "Invalid ASN format" in call[0][0]
                    for call in mock_stderr.call_args_list
                )
            )
