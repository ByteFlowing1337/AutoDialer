import sys
import unittest
from unittest.mock import patch
from autodialer.config import parse_and_save_env_flags


class TestParseAndSaveEnvFlags(unittest.TestCase):
    @patch("autodialer.config.config.dotenv.set_key")
    @patch("autodialer.config.config.os.environ")
    def test_parse_and_save_env_flags(self, mock_environ, mock_set_key):
        # Simulate command-line arguments
        test_args = [
            "script.py",
            "-e",
            "TEST_KEY=TEST_VALUE",
            "--env",
            "ANOTHER_KEY=ANOTHER_VALUE",
        ]
        with patch("sys.argv", test_args):
            parse_and_save_env_flags()

            # Check if set_key was called correctly
            mock_set_key.assert_any_call(".env", "TEST_KEY", "TEST_VALUE")
            mock_set_key.assert_any_call(".env", "ANOTHER_KEY", "ANOTHER_VALUE")

            # Check if environment variables were set
            mock_environ.__setitem__.assert_any_call("TEST_KEY", "TEST_VALUE")
            mock_environ.__setitem__.assert_any_call("ANOTHER_KEY", "ANOTHER_VALUE")

    @patch.object(sys, "argv", ["script.py", "-e"])
    def test_parse_and_save_env_flags_no_env(self):
        # Simulate command-line arguments without env flags
        with self.assertRaises(SystemExit) as context:
            parse_and_save_env_flags()
            self.assertTrue(context.exception.code != 0)

    @patch("autodialer.config.config.logger")
    def test_parse_and_save_env_flags_invalid_format(self, mock_logger):
        # Simulate command-line arguments with invalid env format
        test_args = ["script.py", "-e", "INVALID_FORMAT"]
        # Ensure set_key is not called
        with self.assertRaises(SystemExit) as context:
            with patch("sys.argv", test_args):
                parse_and_save_env_flags()
                self.assertTrue(context.exception.code != 0)
                mock_logger.error.assert_called_with("requires a KEY=VALUE argument")

    @patch("sys.argv", ["script.py", "-e", "KEY=VALUE", "-a", "AS12345"])
    @patch("autodialer.config.config.dotenv.set_key")
    @patch.dict("os.environ", {}, clear=True)
    def test_parse_and_save_env_with_multiple_args_1(self, mock_set_key):
        # Simulate command-line arguments with env flags and other flags
        parse_and_save_env_flags()
        self.assertEqual(sys.argv, ["script.py", "-a", "AS12345"])
        mock_set_key.assert_any_call(".env", "KEY", "VALUE")

    @patch(
        "sys.argv",
        [
            "script.py",
            "-a",
            "AS12345",
            "-e",
            "KEY=VALUE",
        ],
    )
    @patch("autodialer.config.config.dotenv.set_key")
    @patch.dict("os.environ", {}, clear=True)
    def test_parse_and_save_env_with_multiple_args_2(self, mock_set_key):
        # Simulate command-line arguments with env flags and other flags
        parse_and_save_env_flags()
        self.assertEqual(sys.argv, ["script.py", "-a", "AS12345"])
        mock_set_key.assert_any_call(".env", "KEY", "VALUE")

    @patch(
        "sys.argv",
        [
            "script.py",
            "-f",
            "-e",
            "KEY=VALUE",
        ],
    )
    @patch("autodialer.config.config.dotenv.set_key")
    @patch.dict("os.environ", {}, clear=True)
    def test_parse_and_save_env_with_multiple_args_3(self, mock_set_key):
        # Simulate command-line arguments with env flags and other flags
        parse_and_save_env_flags()
        self.assertEqual(sys.argv, ["script.py", "-f"])
        mock_set_key.assert_any_call(".env", "KEY", "VALUE")
