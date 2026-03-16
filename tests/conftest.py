import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(autouse=True)
def _blank_review_url():
    """Ensure google_review_url is empty so tests aren't affected by .env."""
    with patch("app.agent.settings") as mock_settings:
        mock_settings.business_name = "Test Plumbing"
        mock_settings.google_review_url = ""
        mock_settings.gemini_api_key = "fake"
        mock_settings.redis_url = "redis://localhost:6379"
        mock_settings.session_ttl = 86400
        mock_settings.rate_limit_window = 60
        mock_settings.rate_limit_max = 30
        yield mock_settings


@pytest.fixture
def mock_session():
    return {
        "session_id": "test1234",
        "customer_name": "John",
        "plumber_name": "Mike",
        "job_description": "Fixed kitchen sink",
        "device_type": "iphone",
        "status": "contacted",
        "created_at": "2026-03-15T00:00:00Z",
        "message_count": 2,
    }


@pytest.fixture
def mock_redis_fns():
    """Patch all redis_client functions used by agent.py."""
    patches = {}
    fns = [
        "get_session", "update_session", "search_faq", "get_history",
        "add_message", "emit_event", "track_review_event", "publish_notification",
    ]
    started = []
    for fn in fns:
        p = patch(f"app.agent.{fn}", new_callable=AsyncMock)
        patches[fn] = p.start()
        started.append(p)

    yield patches

    for p in started:
        p.stop()


@pytest.fixture
def mock_gemini_client():
    """Patch the genai client in agent.py."""
    with patch("app.agent.client") as mock_client:
        yield mock_client


@pytest.fixture
def gemini_response_text():
    """A simple mock response from Gemini."""
    return "Thanks for choosing us! Would you like to leave a review?"
