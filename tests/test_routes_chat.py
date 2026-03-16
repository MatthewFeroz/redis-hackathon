"""Tests for chat route endpoints."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import ASGITransport, AsyncClient


@pytest.fixture
def mock_agent_and_redis():
    """Patch agent functions and redis rate limiter for route tests."""
    patches = []

    p1 = patch("app.routes_chat.check_rate_limit", new_callable=AsyncMock, return_value=True)
    p2 = patch("app.routes_chat.get_session", new_callable=AsyncMock)

    mock_rate = p1.start()
    mock_get_sess = p2.start()
    patches.extend([p1, p2])

    mock_get_sess.return_value = {
        "session_id": "test1234",
        "customer_name": "John",
        "status": "contacted",
    }

    yield {"check_rate_limit": mock_rate, "get_session": mock_get_sess}

    for p in patches:
        p.stop()


@pytest.fixture
def app():
    """Import app with redis lifespan disabled."""
    from contextlib import asynccontextmanager
    from fastapi import FastAPI

    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    import app.main as main_mod
    main_mod.app.router.lifespan_context = noop_lifespan
    return main_mod.app


@pytest.mark.asyncio
async def test_post_chat_returns_json(app, mock_agent_and_redis):
    from app.agent import ChatResult

    with patch("app.routes_chat.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = ChatResult(reply="Hi there!")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/chat", json={
                "session_id": "test1234",
                "message": "Hello",
                "device_type": "iphone",
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["reply"] == "Hi there!"
        assert data["session_id"] == "test1234"


@pytest.mark.asyncio
async def test_post_chat_stream_returns_sse(app, mock_agent_and_redis):
    async def fake_stream(sid, msg, device_type="unknown"):
        yield {"event": "chunk", "data": json.dumps({"text": "Hello "})}
        yield {"event": "chunk", "data": json.dumps({"text": "world!"})}
        yield {"event": "done", "data": json.dumps({"status": "contacted", "full_reply": "Hello world!"})}

    with patch("app.routes_chat.chat_stream", side_effect=fake_stream):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/chat/stream", json={
                "session_id": "test1234",
                "message": "Hello",
                "device_type": "iphone",
            })

        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
        body = resp.text
        assert "Hello " in body
        assert "world!" in body


@pytest.mark.asyncio
async def test_chat_session_not_found(app):
    with patch("app.routes_chat.check_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("app.routes_chat.get_session", new_callable=AsyncMock, return_value=None):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/chat", json={
                "session_id": "bad_id",
                "message": "Hello",
            })

        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_chat_rate_limited(app):
    with patch("app.routes_chat.check_rate_limit", new_callable=AsyncMock, return_value=False):

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/chat", json={
                "session_id": "test1234",
                "message": "Hello",
            })

        assert resp.status_code == 429
