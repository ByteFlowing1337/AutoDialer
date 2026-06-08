import logging
import time

logger = logging.getLogger(__name__)

GET_ISP_SOURCE_URL = "https://ipinfo.io/json"
ISP_RETRIES = 3
ISP_RETRY_DELAY = 5  # seconds
MAX_ISP_RETRIES = 100


def check_isp(verbose: bool = False) -> str | None:
    """Return the current ISP org string, or ``None`` on failure.

    Network/request and JSON parsing errors are handled internally: a
    diagnostic message is logged and the error does not propagate to
    callers.

    Args:
        verbose: If True, log ``"ISP: <org>"`` on successful lookup.
            This flag does not affect error reporting; error messages are
            always logged on failure.
    """
    import requests

    try:
        response = requests.get(
            GET_ISP_SOURCE_URL, proxies={"http": "", "https": ""}, timeout=5
        )
        response.raise_for_status()
        data = response.json()
        org = data.get("org")
        if not isinstance(org, str):
            logger.error(
                "Unexpected ISP response format: missing or invalid 'org' field."
            )
            return None
        if verbose:
            logger.info("ISP: %s", org)
        return org

    except requests.Timeout:
        logger.error("Timeout while checking ISP. Check your internet connection.")
        return None
    except requests.RequestException as e:
        logger.error("Error checking ISP: %s", e)
        return None
    except ValueError:
        logger.error("Error parsing ISP response.")
        return None


def check_isp_with_retries(
    retries: int = ISP_RETRIES, delay: int = ISP_RETRY_DELAY
) -> str | None:
    """Check the ISP with retries if the initial check fails.

    Args:
        retries: The number of times to retry checking the ISP if it fails.
        delay: The delay in seconds between retries.

    Returns:
        The ISP string if successful, or None if all retries fail.
    """

    if not isinstance(retries, int) or retries < 0 or retries > MAX_ISP_RETRIES:
        logger.error(
            "Invalid retries parameter. Retries must be a non-negative integer."
        )
        return None

    if not isinstance(delay, int) or delay < 0:
        logger.error("Invalid delay parameter. Delay must be a non-negative integer.")
        return None

    for i in range(retries + 1):
        isp = check_isp()
        if isp is not None:
            return isp
        if i < retries:
            time.sleep(delay)

    logger.error("Failed to verify ISP after retries. Check your internet connection.")
    return None
