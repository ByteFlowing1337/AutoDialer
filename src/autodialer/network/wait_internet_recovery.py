import socket
import logging
from time import sleep

logger = logging.getLogger(__name__)


def try_connect(delay: int = 5, attempts: int = 5) -> bool:
    sock = socket.socket()
    for _ in range(attempts):
        if sock.connect_ex(("8.8.8.8", 53)) != 0:
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
    if wait_internet_recovery():
        print("success")
