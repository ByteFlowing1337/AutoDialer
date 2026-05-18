import argparse
import logging
import sys

from autodialer.network import validate_asn

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="AutoDialer is a cross-platform Python CLI package "
        "for router APIs, designed to rotate public IP addresses automatically "
        "and streamline router interactions."
    )
    parser.add_argument(
        "-e",
        "--env",
        metavar="<KEY=VAL>",
        action="append",
        help="Set environment variables (e.g., -e PANEL_PASSWORD=secret)",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force a reconnection regardless of current ASN.",
    )
    group.add_argument(
        "-a",
        "--asn",
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
        sys.exit(0)

    args = parser.parse_args()
    if args.env:
        from autodialer.config import parse_and_save_env_flags

        parse_and_save_env_flags(args.env)

    if args.devices:
        from autodialer.get_devices import print_devices_table

        print_devices_table()
        return

    if args.force or args.asn or args.change:
        from autodialer.reconnection import reconnect

        if args.force:
            reconnect(mode="force")
        elif args.asn:
            reconnect(mode="asn", asn=args.asn)
        elif args.change:
            reconnect(mode="change")
        return


if __name__ == "__main__":
    main()
