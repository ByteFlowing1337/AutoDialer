import socket
from time import sleep


def wait_internet_recovery(delay: int = 5, attempts: int = 5) -> bool:
    sock = socket.socket()
    for _ in range(attempts):
        if not sock.connect_ex(("8.8.8.8", 53)):
            sleep(delay)
        else:
            return True
    return False


if __name__ == "__main__":
    if wait_internet_recovery():
        print("success")
