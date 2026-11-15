import pytest

from src.privacy import redact_pii


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Liên hệ test.user@example.com nhé", "Liên hệ [EMAIL] nhé"),
        ("SĐT 0901234567 gọi sau 5h", "SĐT [PHONE] gọi sau 5h"),
        ("Gọi +84 901 234 567 hoặc 090-123-4567", "Gọi [PHONE] hoặc [PHONE]"),
        ("Số 0901.234.567 nhé", "Số [PHONE] nhé"),
    ],
)
def test_masks_email_and_phone(text, expected):
    assert redact_pii(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Mã căn A0901234567B",
        "Hợp đồng số 12345 ký ngày 01/02/2026",
        "Giá 3 tỷ 200 triệu",
    ],
)
def test_keeps_non_pii_numbers(text):
    assert redact_pii(text) == text


def test_masks_given_customer_name_case_insensitive():
    text = "Anh Nguyễn Văn A phàn nàn, NGUYỄN VĂN A rất bực"

    assert redact_pii(text, "Nguyễn Văn A") == "Anh [NAME] phàn nàn, [NAME] rất bực"


def test_blank_customer_name_is_ignored():
    assert redact_pii("Không có gì cần che", "  ") == "Không có gì cần che"
