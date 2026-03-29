from app.phone_utils import normalize_phone_number


def test_normalize_phone_number_us_formats():
    assert normalize_phone_number("(555) 123-4567") == "+15551234567"
    assert normalize_phone_number("15551234567") == "+15551234567"
    assert normalize_phone_number("+15551234567") == "+15551234567"


def test_normalize_phone_number_handles_empty():
    assert normalize_phone_number("") == ""
