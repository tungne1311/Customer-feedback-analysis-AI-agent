"""Che thông tin định danh trong văn bản trước khi đưa vào phân tích.

Phạm vi hiện tại: email, số điện thoại di động Việt Nam (đầu 0 hoặc +84),
và tên khách hàng khi tên được cung cấp sẵn. Chưa tự phát hiện tên,
địa chỉ, số CCCD hay các định danh khác.
"""

import re

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

PHONE_PATTERN = re.compile(r"(?<!\w)(?:0|\+84)(?:[ .-]?\d){9}(?!\w)")


def redact_pii(text: str, customer_name: str | None = None) -> str:
    text = EMAIL_PATTERN.sub("[EMAIL]", text)
    text = PHONE_PATTERN.sub("[PHONE]", text)

    if customer_name and customer_name.strip():
        name_pattern = r"(?<!\w)" + re.escape(customer_name.strip()) + r"(?!\w)"

        text = re.sub(name_pattern, "[NAME]", text, flags=re.IGNORECASE)

    return text
