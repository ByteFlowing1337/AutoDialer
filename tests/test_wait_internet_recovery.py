import unittest
import importlib
from unittest.mock import patch

try_connect_module = importlib.import_module(
    "autodialer.network.wait_internet_recovery"
)


class TestWaitInternetRecovery(unittest.TestCase):
    @patch.object(try_connect_module, "sleep", return_value=None)
    @patch.object(try_connect_module.socket, "socket")
    def test_wait_internet_recovery_timeout(self, mock_socket, mock_sleep):
        mock_sock = mock_socket.return_value.__enter__.return_value
        mock_sock.connect_ex.return_value = 1
        result = try_connect_module.try_connect(delay=1, attempts=3)
        self.assertFalse(result)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch.object(try_connect_module, "sleep", return_value=None)
    @patch.object(try_connect_module.socket, "socket")
    def test_wait_internet_recovery_success(self, mock_socket, mock_sleep):
        mock_sock = mock_socket.return_value.__enter__.return_value
        mock_sock.connect_ex.return_value = 0
        result = try_connect_module.try_connect()
        self.assertTrue(result)

    @patch.object(try_connect_module, "sleep", return_value=None)
    @patch.object(try_connect_module.socket, "socket")
    def test_wait_internet_recovery_last_attempt_not_sleep(
        self, mock_socket, mock_sleep
    ):
        mock_sock = mock_socket.return_value.__enter__.return_value
        mock_sock.connect_ex.return_value = 1
        result = try_connect_module.try_connect(delay=1, attempts=1)
        self.assertFalse(result)
        self.assertEqual(mock_sleep.call_count, 0)


if __name__ == "__main__":
    unittest.main()
