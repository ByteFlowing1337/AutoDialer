def is_target_asn(current_isp: str | None, target_asn: str | None) -> bool:
    if not target_asn or not isinstance(current_isp, str):
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


def normalize_asn(asn: str) -> str:
    raw_asn = asn.strip().upper()
    if not raw_asn.startswith("AS"):
        raw_asn = "AS" + raw_asn
    if len(raw_asn) > 2 and len(raw_asn) < 10 and raw_asn[2:].strip().isdigit():
        return raw_asn
    return ""
