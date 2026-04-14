import requests
import logging

logger = logging.getLogger(__name__)


def get_ip_address() -> str | None:
    api_sources = [
        "https://ipinfo.io/ip",
        "https://ifconfig.me/ip",
        "https://api.ipify.org",
    ]

    for source in api_sources:
        try:
            response = requests.get(
                source, proxies={"http": "", "https": ""}, timeout=5
            )
            response.raise_for_status()
            ip: str = response.text.replace("\n", "").replace(" ", "")
            return ip
        except requests.RequestException as e:
            logger.error("Error fetching IP address from %s: %s", source, e)

    logger.error("All attempts to fetch IP address failed.")
    return None


if __name__ == "__main__":
    get_ip_address()
