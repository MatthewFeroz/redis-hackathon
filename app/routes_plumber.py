"""
Plumber-facing routes: dashboard, job creation, analytics, SSE notifications.
"""

import asyncio
import json
import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

from app.models import AnalyticsResponse, JobCreate, JobResponse
from app.sms import send_review_link
from app.redis_client import (
    create_session,
    get_all_sessions,
    get_analytics,
    get_daily_counts,
    get_events,
    get_funnel_counts,
    get_history,
    get_redis_stats,
    subscribe_notifications,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard_page():
    build_index = os.path.join("dashboard-app", "build", "index.html")
    if os.path.exists(build_index):
        with open(build_index) as f:
            return HTMLResponse(f.read())
    with open("static/dashboard.html") as f:
        return HTMLResponse(f.read())


@router.post("/api/jobs", response_model=JobResponse)
async def create_job(body: JobCreate, request: Request):
    session_id = await create_session(
        customer_name=body.customer_name,
        customer_phone=body.customer_phone,
        customer_email=body.customer_email,
        customer_address=body.customer_address,
        customer_zip=body.customer_zip,
        referral_source=body.referral_source,
        job_description=body.job_description,
        job_type=body.job_type,
        job_total=body.job_total,
        job_date=body.job_date,
        plumber_name=body.plumber_name,
        is_repeat_customer=body.is_repeat_customer,
        follow_up_notes=body.follow_up_notes,
    )
    base_url = str(request.base_url).rstrip("/")
    review_link = f"{base_url}/review/{session_id}"

    # Send SMS if phone number provided
    sms_result = await send_review_link(
        to_phone=body.customer_phone,
        customer_name=body.customer_name,
        review_link=review_link,
        plumber_name=body.plumber_name,
    )

    return JobResponse(
        session_id=session_id,
        review_link=review_link,
        sms_sent=sms_result.get("sent", False),
        sms_error=sms_result.get("error"),
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


@router.get("/api/sessions/{session_id}/history")
async def session_history(session_id: str):
    return await get_history(session_id)


@router.get("/api/analytics/detailed")
async def analytics_detailed():
    base = await get_analytics()
    funnel = await get_funnel_counts()
    daily_reviews = await get_daily_counts("review_submitted", 7)
    daily_started = await get_daily_counts("review_started", 7)
    sessions = await get_all_sessions()
    total_messages = sum(s.get("message_count", 0) for s in sessions)
    avg_messages = round(total_messages / len(sessions), 1) if sessions else 0
    return {
        **base,
        "funnel": funnel,
        "daily_reviews": daily_reviews,
        "daily_started": daily_started,
        "avg_messages": avg_messages,
    }


@router.get("/api/redis-stats")
async def redis_stats():
    return await get_redis_stats()


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
