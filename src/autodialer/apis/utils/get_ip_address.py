import requests
import logging

logger = logging.getLogger(__name__)


def get_ip_address() -> str | None:
    try:
        response = requests.get(
            "https://api.ipify.org", proxies={"http": "", "https": ""}, timeout=5
        )
        response.raise_for_status()
        ip: str = response.text.replace("\n", "").replace(" ", "")
        return ip
    except requests.RequestException as e:
        logger.error(f"Error fetching IP address: {e}")
        return None
