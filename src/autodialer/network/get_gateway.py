import ipaddress
import logging
import socket
import struct
import sys

logger = logging.getLogger(__name__)


def _is_ip_address(value: str) -> bool:
    try:
        ipaddress.ip_address(value.split("%", 1)[0])
        return True
    except ValueError:
        return False


def _extract_first_ip(tokens: list[str]) -> str | None:
    for token in tokens:
        candidate = token.strip()
        if _is_ip_address(candidate):
            return candidate
    return None


def format_ip_for_url_host(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        return candidate

    if candidate.startswith("[") and candidate.endswith("]"):
        candidate = candidate[1:-1]

    address_part = candidate
    zone_id: str | None = None
    zone_is_encoded = False
    if "%25" in candidate:
        address_part, zone_id = candidate.split("%25", 1)
        zone_is_encoded = True
    elif "%" in candidate:
        address_part, zone_id = candidate.split("%", 1)

    try:
        parsed = ipaddress.ip_address(address_part)
    except ValueError:
        return value

    if isinstance(parsed, ipaddress.IPv6Address):
        if zone_id is not None:
            from urllib.parse import quote

            encoded_zone = zone_id if zone_is_encoded else quote(zone_id, safe="")
            return f"[{parsed.compressed}%25{encoded_zone}]"
        return f"[{parsed.compressed}]"
    return parsed.compressed


def _get_gateway_ip_unsupported() -> str:
    logger.error(
        "Unsupported platform. Cannot determine default gateway IP address.",
    )
    sys.exit(1)


def get_gateway_ip_on_windows() -> str:
    try:
        import subprocess

        result = subprocess.run(
            ["route", "print", "-4"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as e:
        logger.error("Failed to execute 'route print -4': %s", e)
        sys.exit(1)

    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 3:
            continue
        if fields[0] == "0.0.0.0" and fields[1] == "0.0.0.0":
            gateway = fields[2]
            if _is_ip_address(gateway):
                return gateway
    logger.error("Default gateway not found in 'route print -4' output.")
    sys.exit(1)


def get_gateway_ip_on_linux() -> str:
    try:
        with open("/proc/net/route", encoding="utf-8") as routes:
            next(routes, None)
            for line in routes:
                fields = line.strip().split()
                if len(fields) < 4:
                    continue

                destination, gateway_hex, flags_hex = fields[1], fields[2], fields[3]
                if destination != "00000000":
                    continue

                flags = int(flags_hex, 16)
                if not flags & 0x2:
                    continue

                gateway = socket.inet_ntoa(struct.pack("<L", int(gateway_hex, 16)))
                if gateway != "0.0.0.0":
                    return gateway
    except (OSError, ValueError):
        pass

    try:
        import subprocess

        result = subprocess.run(
            ["ip", "-4", "route", "show", "default"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as e:
        logger.error("Failed to execute 'ip -4 route show default': %s", e)
        sys.exit(1)

    for line in result.stdout.splitlines():
        fields = line.split()
        if not fields or fields[0] != "default":
            continue

        if "via" in fields:
            via_index = fields.index("via") + 1
            if via_index < len(fields):
                via_gateway = fields[via_index]
                if _is_ip_address(via_gateway):
                    return via_gateway

        parsed_gateway = _extract_first_ip(fields[1:])
        if parsed_gateway is not None:
            return parsed_gateway
    logger.error("Default gateway not found in 'ip -4 route show default' output.")
    sys.exit(1)


def get_gateway_ip_on_unix() -> str:
    try:
        import subprocess

        result = subprocess.run(
            ["route", "-n", "get", "default"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as e:
        logger.error("Failed to execute 'route -n get default': %s", e)
        sys.exit(1)

    if result is not None:
        for line in result.stdout.splitlines():
            _, _, value = line.partition(":")
            if not value:
                continue
            gateway = _extract_first_ip(value.split())
            if gateway is not None:
                return gateway

    try:
        result = subprocess.run(
            ["netstat", "-rn"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as e:
        logger.error("Failed to execute 'netstat -rn': %s", e)
        sys.exit(1)

    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) < 2:
            continue

        destination = fields[0].lower()
        if destination not in {"default", "0.0.0.0", "::/0"}:
            continue

        gateway = _extract_first_ip(fields[1:])
        if gateway is not None:
            return gateway
    logger.error(
        "Default gateway not found in 'route -n get default' or 'netstat -rn' output."
    )
    sys.exit(1)


def get_gateway_ip() -> str:
    import platform

    platform_system = platform.system()
    if platform_system == "Windows":
        return get_gateway_ip_on_windows()
    elif platform_system == "Linux":
        return get_gateway_ip_on_linux()
    elif platform_system in {"Darwin", "FreeBSD", "OpenBSD", "NetBSD", "Unix"}:
        return get_gateway_ip_on_unix()
    else:
        return _get_gateway_ip_unsupported()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    gateway_ip = get_gateway_ip()
    if gateway_ip:
        logger.info("Default Gateway IP: %s", gateway_ip)
    else:
        logger.error("Could not determine the default gateway IP address.")
