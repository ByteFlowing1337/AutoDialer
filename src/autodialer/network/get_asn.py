from autodialer.utils import normalize_asn


def is_target_asn(current_isp: str | None, target_asn: str | None) -> bool:
    if not target_asn or not isinstance(target_asn, str):
        return False
    if not current_isp or not isinstance(current_isp, str):
        return False
    target_asn = normalize_asn(target_asn)
    if not target_asn:
        return False

    tokens = current_isp.split()
    if not tokens:
        return False
    first_token = normalize_asn(tokens[0])
    if not first_token:
        return False

    return first_token == target_asn
