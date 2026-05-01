import socket
import logging
from time import sleep

logger = logging.getLogger(__name__)


def try_connect(delay: int = 5, attempts: int = 10) -> bool:
    """Attempts to connect to a well-known public DNS server to verify internet connectivity.

    Args:
        delay:  Time in seconds to wait between connection attempts.
        attempts:  Number of connection attempts before giving up.

    Returns:
        True if a connection was successfully established, False otherwise.
    """
    for attempt in range(attempts):
        with socket.socket() as sock:
            sock.settimeout(5)
            # Using TUN mode proxy will immediately return success here,
            # but we have no way to detect at that level.
            connected = sock.connect_ex(("8.8.8.8", 53)) == 0
        if connected:
            return True
        if attempt < attempts - 1:
            sleep(delay)
    return False


# For debugging
if __name__ == "__main__":
    if try_connect():
        print("success")
