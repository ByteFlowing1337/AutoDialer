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


def normalize_asn(asn: str) -> str:
    raw_asn = asn.strip().upper()
    if raw_asn.startswith("AS"):
        digits = raw_asn[2:].strip()
    else:
        digits = raw_asn.strip()

    if digits.isdigit():
        asn_num = int(digits)
        # Valid 32-bit ASN range is 1 to 4294967295
        # See https://www.iana.org/assignments/as-numbers/as-numbers.xhtml
        if 1 <= asn_num <= 4294967295:
            return f"AS{asn_num}"

    return ""
