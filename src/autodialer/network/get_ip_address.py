import ipaddress
import logging

logger = logging.getLogger(__name__)

GET_IP_ADDRESS_SOURCE_URLS = [
    "https://icanhazip.com",
    "https://ipinfo.io/ip",
    "https://ifconfig.me/ip",
    "https://api.ipify.org",
]


def get_ip_address() -> str | None:
    import requests

    for source in GET_IP_ADDRESS_SOURCE_URLS:
        try:
            response = requests.get(
                source, proxies={"http": "", "https": ""}, timeout=5
            )
            response.raise_for_status()
            ip: str = response.text.strip()
            if ipaddress.ip_address(ip):
                return ip
        except requests.RequestException as e:
            logger.error("Error fetching IP address from %s: %s", source, e)

    logger.error("All attempts to fetch IP address failed.")
    return None


if __name__ == "__main__":
    get_ip_address()
