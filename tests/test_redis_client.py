import string

from app.redis_client import generate_session_id


def test_generate_session_id_returns_long_urlsafe_token():
    token = generate_session_id()

    allowed = set(string.ascii_letters + string.digits + "-_")

    assert len(token) >= 32
    assert set(token) <= allowed


def test_generate_session_id_is_unique_across_calls():
    first = generate_session_id()
    second = generate_session_id()

    assert first != second
