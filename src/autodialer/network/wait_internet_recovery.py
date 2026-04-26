import socket
import logging
from time import sleep

logger = logging.getLogger(__name__)


def try_connect(delay: int = 5, attempts: int = 5) -> bool:
    for _ in range(attempts):
        # Use a short-lived socket per probe so descriptors are always closed.
        with socket.socket() as sock:
            connected = sock.connect_ex(("8.8.8.8", 53)) == 0

        if not connected:
            sleep(delay)
        else:
            return True
    return False


def wait_internet_recovery(delay: int = 5, attempts: int = 5) -> None:
    if try_connect(delay, attempts):
        return
    else:
        logger.error("Internet did not recover within the expected time.")
        return


if __name__ == "__main__":
    if try_connect():
        print("success")
