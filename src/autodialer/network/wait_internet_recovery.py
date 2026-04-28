import socket
import logging
from time import sleep

logger = logging.getLogger(__name__)


def try_connect(delay: int = 5, attempts: int = 3) -> bool:
    for _ in range(attempts):
        with socket.socket() as sock:
            sock.settimeout(delay)
            connected = sock.connect_ex(("8.8.8.8", 53)) == 0
        if connected:
            return True
        sleep(delay)
    return False


def wait_internet_recovery(delay: int = 5, attempts: int = 3) -> None:
    if try_connect(delay, attempts):
        return
    else:
        logger.error("Internet did not recover within the expected time.")
        return


# For debugging purposes
if __name__ == "__main__":
    if try_connect():
        print("success")
