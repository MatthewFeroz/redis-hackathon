"""Phone normalization helpers shared across SMS flows."""


def normalize_phone_number(phone: str) -> str:
    if not phone:
        return ""

    normalized = (
        phone.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    if not normalized:
        return ""

    if normalized.startswith("+"):
        return normalized

    if normalized.startswith("1") and len(normalized) == 11:
        return f"+{normalized}"

    if len(normalized) == 10:
        return f"+1{normalized}"

    return f"+{normalized}"
