import unittest
from unittest.mock import patch
from autodialer.config import parse_and_save_env_flags, get_env_file_path


class TestParseAndSaveEnvFlags(unittest.TestCase):
    @patch("autodialer.config.config.dotenv.set_key")
    @patch("autodialer.config.config.os.environ")
    @patch("autodialer.config.config.Path")
    def test_parse_and_save_env_with_e_flags(
        self, mock_path, mock_environ, mock_set_key
    ):
        mock_path.return_value.exists.return_value = True

        env_args = ["TEST_KEY=TEST_VALUE", "ANOTHER_KEY=ANOTHER_VALUE"]
        parse_and_save_env_flags(env_args)

        mock_set_key.assert_any_call(str(get_env_file_path()), "TEST_KEY", "TEST_VALUE")
        mock_set_key.assert_any_call(
            str(get_env_file_path()), "ANOTHER_KEY", "ANOTHER_VALUE"
        )

        mock_environ.__setitem__.assert_any_call("TEST_KEY", "TEST_VALUE")
        mock_environ.__setitem__.assert_any_call("ANOTHER_KEY", "ANOTHER_VALUE")

    @patch("autodialer.config.config.logger")
    def test_parse_and_save_env_flags_no_env_value(self, mock_logger):
        with self.assertRaises(SystemExit) as context:
            parse_and_save_env_flags(["PANEL_PASSWORD="])
        self.assertTrue(context.exception.code != 0)
        mock_logger.error.assert_called_with(
            "Error: -e/--env requires a KEY=VALUE argument (e.g., -e PANEL_PASSWORD=secret)."
        )

    @patch("autodialer.config.config.logger")
    def test_parse_and_save_env_flags_invalid_format(self, mock_logger):
        with self.assertRaises(SystemExit) as context:
            parse_and_save_env_flags(["INVALID_FORMAT"])
        self.assertTrue(context.exception.code != 0)
        mock_logger.error.assert_called_with(
            "Error: -e/--env requires a KEY=VALUE argument (e.g., -e PANEL_PASSWORD=secret)."
        )
