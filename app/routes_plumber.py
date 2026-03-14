"""
Plumber-facing routes: dashboard, job creation, analytics, SSE notifications.
"""

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

from app.models import AnalyticsResponse, JobCreate, JobResponse
from app.redis_client import (
    create_session,
    get_all_sessions,
    get_analytics,
    get_events,
    subscribe_notifications,
)

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    with open("static/dashboard.html") as f:
        return HTMLResponse(f.read())


@router.post("/api/jobs", response_model=JobResponse)
async def create_job(body: JobCreate, request: Request):
    session_id = await create_session(
        customer_name=body.customer_name,
        customer_phone=body.customer_phone,
        customer_email=body.customer_email,
        job_description=body.job_description,
        plumber_name=body.plumber_name,
    )
    base_url = str(request.base_url).rstrip("/")
    return JobResponse(
        session_id=session_id,
        review_link=f"{base_url}/review/{session_id}",
    )


@router.get("/api/sessions")
async def list_sessions():
    sessions = await get_all_sessions()
    sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return sessions


@router.get("/api/analytics", response_model=AnalyticsResponse)
async def analytics():
    data = await get_analytics()
    return AnalyticsResponse(**data)


@router.get("/api/events")
async def events(count: int = 50):
    return await get_events(count)


@router.get("/api/notifications")
async def notifications(request: Request):
    """SSE endpoint — streams Redis Pub/Sub messages to the plumber dashboard."""

    async def event_stream():
        pubsub = await subscribe_notifications()
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message and message["type"] == "message":
                    yield {"event": "notification", "data": message["data"]}
                else:
                    yield {"event": "ping", "data": ""}
                    await asyncio.sleep(2)
        finally:
            await pubsub.unsubscribe("plumber:notifications")
            await pubsub.aclose()

    return EventSourceResponse(event_stream())
