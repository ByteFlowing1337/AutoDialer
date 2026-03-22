from sys import argv
import apis


if __name__ == "__main__":
    if len(argv) == 1:
        apis.tplink_get_devices()
        