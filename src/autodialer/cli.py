import argparse
import sys

from autodialer import __version__
from autodialer.utils import validate_asn


def main():
    parser = argparse.ArgumentParser(
        description="AutoDialer is a cross-platform Python CLI package "
        "for router APIs, designed to rotate public IP addresses automatically "
        "and streamline router interactions."
    )
    parser.add_argument(
        "-e",
        "--env",
        action="append",
        metavar="<KEY=VAL>",
        help="Set environment variables (e.g., -e PANEL_PASSWORD=secret)",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"AutoDialer {__version__}",
        help="Show the current version of AutoDialer",
    )

    parser.add_argument(
        "-n",
        "--attempts",
        action="store",
        default=5,
        metavar="<N>",
        type=int,
        help="Number of reconnection attempts before giving up (default: 5)",
    )

    # Remove required=True because `-e` can be used individually
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force a reconnection regardless of current ASN.",
    )
    group.add_argument(
        "-a",
        "--asn",
        action="store",
        metavar="<ASN>",
        type=validate_asn,
        help="Reconnect until connected to the specified target ASN.",
    )
    group.add_argument(
        "-c",
        "--change",
        action="store_true",
        help="Reconnect until the public IP address changes.",
    )
    group.add_argument(
        "-d",
        "--devices",
        action="store_true",
        help="Display connected devices.",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()
    if args.env:
        from autodialer.config import parse_and_save_env_flags

        if not parse_and_save_env_flags(args.env):
            sys.exit(1)
        print("Environment variables updated successfully.")
        return

    if args.devices:
        from autodialer.get_devices import print_devices_table

        try:
            print_devices_table()
        except RuntimeError as e:
            # Lazy import logging as it has a not low overhead, and
            # should never be used when the user just wants
            # to see the help message or print devices
            # See https://github.com/python/cpython/pull/150073
            import logging

            logger = logging.getLogger(__name__)
            logger.error(str(e))
            sys.exit(1)
        return

    if args.force or args.asn or args.change:
        from autodialer.reconnection import reconnect

        try:
            if args.force:
                reconnect(mode="force", max_attempts=args.attempts)
            elif args.asn:
                reconnect(mode="asn", asn=args.asn, max_attempts=args.attempts)
            elif args.change:
                reconnect(mode="change", max_attempts=args.attempts)
        except RuntimeError as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(str(e))
            sys.exit(1)
        return


if __name__ == "__main__":
    main()
