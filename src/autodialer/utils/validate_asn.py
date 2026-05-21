def normalize_asn(asn: str) -> str:
    raw_asn = asn.strip().upper()
    digits = raw_asn[2:].strip() if raw_asn.startswith("AS") else raw_asn.strip()

    if digits.isdigit():
        asn_num = int(digits)
        # Valid 32-bit ASN range is 1 to 4294967295
        # See https://www.iana.org/assignments/as-numbers/as-numbers.xhtml
        if 1 <= asn_num <= 4294967295:
            return f"AS{asn_num}"

    return ""


def validate_asn(value: str) -> str:
    normalized = normalize_asn(value)
    if not normalized:
        import argparse

        raise argparse.ArgumentTypeError(
            f"Invalid ASN format: '{value}'. Valid range is AS1 to AS4294967295."
        )
    return normalized
