import re


EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

PHONE_PATTERN = r"(?<!\w)(?:0|\+84)(?:[ .-]?\d){9}(?!\w)"


def redact_pii(text, customer_name=None):
    text = re.sub(EMAIL_PATTERN, "[EMAIL]", text)
    text = re.sub(PHONE_PATTERN, "[PHONE]", text)

    if customer_name and customer_name.strip():
        name_pattern = (
            r"(?<!\w)"
            + re.escape(customer_name.strip())
            + r"(?!\w)"
        )

        text = re.sub(
            name_pattern,
            "[NAME]",
            text,
            flags=re.IGNORECASE,
        )

    return text