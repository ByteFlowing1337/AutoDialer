import logging
import requests


logger = logging.getLogger(__name__)


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
    try:
        response = requests.get(
            "https://ipinfo.io/json", proxies={"http": "", "https": ""}, timeout=5
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


def check_isp_with_retries(retries: int = 3) -> str | None:
    """Check the ISP with retries if the initial check fails.

    Args:
        retries: The number of times to retry checking the ISP if it fails.

    Returns:
        The ISP string if successful, or None if all retries fail.
    """

    if retries <= 0:
        logger.error("Invalid retries parameter. Retries must be a positive integer.")
        return None

    for _ in range(retries):
        isp = check_isp()
        if isp is not None:
            return isp

    logger.error("Failed to verify ISP after retries. Check your internet connection.")
    return None
