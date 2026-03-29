"""Tests for Twilio-style webhook routes."""

import pytest
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app():
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    import app.main as main_mod

    main_mod.app.router.lifespan_context = noop_lifespan
    return main_mod.app


@pytest.mark.asyncio
async def test_inbound_stop_marks_phone_opted_out(app):
    with patch("app.routes_sms.set_sms_opt_out", new_callable=AsyncMock) as mock_set_opt_out, \
         patch("app.routes_sms.get_sessions_by_phone", new_callable=AsyncMock, return_value=[
             {"session_id": "sess_1", "organization_id": "org_1"}
         ]), \
         patch("app.routes_sms.update_session", new_callable=AsyncMock) as mock_update, \
         patch("app.routes_sms.emit_event", new_callable=AsyncMock) as mock_emit, \
         patch("app.routes_sms.settings") as mock_settings:
        mock_settings.business_name = "Test Plumbing"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(
                "/webhooks/twilio/inbound",
                data={"From": "(555) 123-4567", "Body": "STOP", "MessageSid": "SM123"},
            )

    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    assert "unsubscribed" in resp.text.lower()
    mock_set_opt_out.assert_awaited_once()
    mock_update.assert_awaited_once()
    mock_emit.assert_awaited_once()


@pytest.mark.asyncio
async def test_inbound_help_returns_support_message(app):
    with patch("app.routes_sms.settings") as mock_settings:
        mock_settings.business_name = "Test Plumbing"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(
                "/webhooks/twilio/inbound",
                data={"From": "+15551234567", "Body": "HELP", "MessageSid": "SM456"},
            )

    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    assert "reply stop to opt out" in resp.text.lower()


@pytest.mark.asyncio
async def test_status_callback_updates_matching_session(app):
    with patch("app.routes_sms.find_session_by_sms_sid", new_callable=AsyncMock, return_value={
        "session_id": "sess_1",
        "organization_id": "org_1",
        "sms_message_sid": "SM123",
    }), \
         patch("app.routes_sms.update_session", new_callable=AsyncMock) as mock_update, \
         patch("app.routes_sms.emit_event", new_callable=AsyncMock) as mock_emit:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(
                "/webhooks/twilio/status",
                data={
                    "MessageSid": "SM123",
                    "MessageStatus": "delivered",
                    "To": "+15551234567",
                    "ErrorCode": "",
                    "ErrorMessage": "",
                },
            )

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    mock_update.assert_awaited_once()
    mock_emit.assert_awaited_once()
