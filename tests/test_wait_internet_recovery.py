import importlib
import unittest
from unittest.mock import patch

get_internet_connectivity_module = importlib.import_module(
    "autodialer.network.get_connectivity"
)


class TestWaitInternetRecovery(unittest.TestCase):
    @patch.object(get_internet_connectivity_module, "sleep", return_value=None)
    @patch.object(get_internet_connectivity_module.socket, "socket")
    def test_get_connectivity_timeout(self, mock_socket, mock_sleep):
        mock_sock = mock_socket.return_value.__enter__.return_value
        mock_sock.connect_ex.return_value = 1
        result = get_internet_connectivity_module.get_internet_connectivity(
            delay=1, attempts=3
        )
        self.assertFalse(result)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch.object(get_internet_connectivity_module, "sleep", return_value=None)
    @patch.object(get_internet_connectivity_module.socket, "socket")
    def test_get_connectivity_success(self, mock_socket, mock_sleep):
        mock_sock = mock_socket.return_value.__enter__.return_value
        mock_sock.connect_ex.return_value = 0
        result = get_internet_connectivity_module.get_internet_connectivity()
        self.assertTrue(result)

    @patch.object(get_internet_connectivity_module, "sleep", return_value=None)
    @patch.object(get_internet_connectivity_module.socket, "socket")
    def test_get_connectivity_last_attempt_not_sleep(self, mock_socket, mock_sleep):
        mock_sock = mock_socket.return_value.__enter__.return_value
        mock_sock.connect_ex.return_value = 1
        result = get_internet_connectivity_module.get_internet_connectivity(
            delay=1, attempts=1
        )
        self.assertFalse(result)
        self.assertEqual(mock_sleep.call_count, 0)


if __name__ == "__main__":
    unittest.main()
