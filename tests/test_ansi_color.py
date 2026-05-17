import unittest
from unittest.mock import patch


class TestAnsiColor(unittest.TestCase):
    @patch("sys.stdout.isatty", return_value=True)
    def test_ansi_colors_enabled(self, mock_isatty):
        from autodialer.utils import CYAN, GREEN, YELLOW, RED, RESET

        self.assertEqual(CYAN, "\033[96m")
        self.assertEqual(GREEN, "\033[92m")
        self.assertEqual(YELLOW, "\033[93m")
        self.assertEqual(RED, "\033[91m")
        self.assertEqual(RESET, "\033[0m")

    @patch("sys.stdout.isatty", return_value=False)
    def test_ansi_colors_disabled(self, mock_isatty):
        from autodialer.utils import CYAN, GREEN, YELLOW, RED, RESET

        self.assertEqual(CYAN, "")
        self.assertEqual(GREEN, "")
        self.assertEqual(YELLOW, "")
        self.assertEqual(RED, "")
        self.assertEqual(RESET, "")
