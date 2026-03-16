"""Tests for agent chat and chat_stream functions."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agent import chat, chat_stream


@pytest.mark.asyncio
async def test_chat_returns_reply(mock_redis_fns, mock_gemini_client, mock_session, gemini_response_text):
    mock_redis_fns["get_session"].return_value = mock_session
    mock_redis_fns["search_faq"].return_value = []
    mock_redis_fns["get_history"].return_value = []

    resp = MagicMock()
    resp.text = gemini_response_text
    mock_gemini_client.aio.models.generate_content = AsyncMock(return_value=resp)

    result = await chat("test1234", "Hello!")
    assert result.reply == gemini_response_text
    assert result.timings is None  # profiling off by default


@pytest.mark.asyncio
async def test_chat_with_profiling(mock_redis_fns, mock_gemini_client, mock_session, gemini_response_text):
    mock_redis_fns["get_session"].return_value = mock_session
    mock_redis_fns["search_faq"].return_value = []
    mock_redis_fns["get_history"].return_value = []

    resp = MagicMock()
    resp.text = gemini_response_text
    mock_gemini_client.aio.models.generate_content = AsyncMock(return_value=resp)

    result = await chat("test1234", "Hello!", profile=True)
    assert result.timings is not None
    assert "gemini_generate" in result.timings
    assert "get_session" in result.timings
    assert all(v >= 0 for v in result.timings.values())


@pytest.mark.asyncio
async def test_chat_session_not_found(mock_redis_fns, mock_gemini_client):
    mock_redis_fns["get_session"].return_value = None

    result = await chat("bad_id", "Hello!")
    assert "couldn't find" in result.reply.lower()


@pytest.mark.asyncio
async def test_chat_detects_submitted(mock_redis_fns, mock_gemini_client, mock_session, gemini_response_text):
    mock_redis_fns["get_session"].return_value = mock_session
    mock_redis_fns["search_faq"].return_value = []
    mock_redis_fns["get_history"].return_value = []

    resp = MagicMock()
    resp.text = gemini_response_text
    mock_gemini_client.aio.models.generate_content = AsyncMock(return_value=resp)

    await chat("test1234", "I just posted the review!")
    mock_redis_fns["update_session"].assert_any_call("test1234", status="submitted")
    mock_redis_fns["publish_notification"].assert_called_once()


@pytest.mark.asyncio
async def test_chat_detects_declined(mock_redis_fns, mock_gemini_client, mock_session, gemini_response_text):
    mock_redis_fns["get_session"].return_value = mock_session
    mock_redis_fns["search_faq"].return_value = []
    mock_redis_fns["get_history"].return_value = []

    resp = MagicMock()
    resp.text = gemini_response_text
    mock_gemini_client.aio.models.generate_content = AsyncMock(return_value=resp)

    await chat("test1234", "no thanks")
    mock_redis_fns["update_session"].assert_any_call("test1234", status="declined")


@pytest.mark.asyncio
async def test_chat_stream_yields_chunks(mock_redis_fns, mock_gemini_client, mock_session):
    mock_redis_fns["get_session"].return_value = mock_session
    mock_redis_fns["search_faq"].return_value = []
    mock_redis_fns["get_history"].return_value = []

    # Mock streaming response
    chunk1 = MagicMock()
    chunk1.text = "Thanks "
    chunk2 = MagicMock()
    chunk2.text = "for choosing "
    chunk3 = MagicMock()
    chunk3.text = "us!"

    async def fake_stream():
        for c in [chunk1, chunk2, chunk3]:
            yield c

    mock_gemini_client.aio.models.generate_content_stream = AsyncMock(return_value=fake_stream())

    events = []
    async for event in chat_stream("test1234", "Hello!"):
        events.append(event)

    chunk_events = [e for e in events if e["event"] == "chunk"]
    done_events = [e for e in events if e["event"] == "done"]

    assert len(chunk_events) == 3
    assert len(done_events) == 1

    # Verify chunks contain the right text
    assert json.loads(chunk_events[0]["data"])["text"] == "Thanks "
    assert json.loads(chunk_events[1]["data"])["text"] == "for choosing "
    assert json.loads(chunk_events[2]["data"])["text"] == "us!"

    # Verify done event has full reply
    done_data = json.loads(done_events[0]["data"])
    assert done_data["full_reply"] == "Thanks for choosing us!"


@pytest.mark.asyncio
async def test_chat_stream_persists_messages(mock_redis_fns, mock_gemini_client, mock_session):
    mock_redis_fns["get_session"].return_value = mock_session
    mock_redis_fns["search_faq"].return_value = []
    mock_redis_fns["get_history"].return_value = []

    chunk = MagicMock()
    chunk.text = "Hello!"

    async def fake_stream():
        yield chunk

    mock_gemini_client.aio.models.generate_content_stream = AsyncMock(return_value=fake_stream())

    async for _ in chat_stream("test1234", "Hi"):
        pass

    # Should save both user and assistant messages
    calls = mock_redis_fns["add_message"].call_args_list
    assert len(calls) == 2
    assert calls[0].args == ("test1234", "user", "Hi")
    assert calls[1].args == ("test1234", "assistant", "Hello!")


@pytest.mark.asyncio
async def test_chat_stream_session_not_found(mock_redis_fns, mock_gemini_client):
    mock_redis_fns["get_session"].return_value = None

    events = []
    async for event in chat_stream("bad_id", "Hello!"):
        events.append(event)

    assert len(events) == 1
    assert events[0]["event"] == "error"
