"""
Plumber-facing routes: dashboard, job creation, analytics, SSE notifications.
"""

import asyncio
import json
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse

from app.auth import AuthContext, require_role, require_session
from app.geocoding import geocode_location
from app.models import AnalyticsResponse, CustomerMapPoint, JobCreate, JobResponse
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
    get_session,
    subscribe_notifications,
    update_session,
)

router = APIRouter()


def _target_org(context: AuthContext, requested: str | None) -> str | None:
    if context.is_superadmin:
        if requested in (None, "", "all"):
            return context.organization_id
        return requested
    return context.organization_id


@router.get("/", response_class=HTMLResponse)
async def dashboard_page():
    build_index = os.path.join("dashboard-app", "build", "index.html")
    if os.path.exists(build_index):
        with open(build_index) as f:
            return HTMLResponse(f.read())
    with open("static/dashboard.html") as f:
        return HTMLResponse(f.read())


@router.post("/api/jobs", response_model=JobResponse)
async def create_job(
    body: JobCreate,
    request: Request,
    context: AuthContext = Depends(require_role("owner", "admin")),
):
    if context.organization_id is None:
        raise HTTPException(status_code=400, detail="Select an organization before creating a job")
    session_id = await create_session(
        organization_id=context.organization_id,
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
        created_by_user_id=context.user_id,
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
async def list_sessions(
    organization_id: str | None = None,
    context: AuthContext = Depends(require_session),
):
    sessions = await get_all_sessions(_target_org(context, organization_id))
    sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return sessions


@router.get("/api/customers/map", response_model=list[CustomerMapPoint])
async def customer_map_points(
    organization_id: str | None = None,
    context: AuthContext = Depends(require_session),
):
    target_org = _target_org(context, organization_id)
    sessions = await get_all_sessions(target_org)
    points: list[CustomerMapPoint] = []

    async def resolve_session(session: dict) -> CustomerMapPoint | None:
        latitude = session.get("latitude")
        longitude = session.get("longitude")
        geocode_source = session.get("geocode_source", "")

        if latitude is None or longitude is None:
            geocoded = await geocode_location(
                session.get("customer_address", ""),
                session.get("customer_zip", ""),
            )
            if geocoded and "latitude" in geocoded and "longitude" in geocoded:
                latitude = geocoded["latitude"]
                longitude = geocoded["longitude"]
                geocode_source = geocoded.get("geocode_source", "")
                await update_session(
                    session["session_id"],
                    latitude=latitude,
                    longitude=longitude,
                    geocode_source=geocode_source,
                    geocode_error="",
                )
            elif geocoded and geocoded.get("geocode_error"):
                await update_session(
                    session["session_id"],
                    geocode_error=geocoded["geocode_error"],
                )
                return None
            else:
                return None

        return CustomerMapPoint(
            session_id=session["session_id"],
            organization_id=session.get("organization_id"),
            customer_name=session.get("customer_name", ""),
            customer_address=session.get("customer_address", ""),
            customer_zip=session.get("customer_zip", ""),
            status=session.get("status", "created"),
            latitude=latitude,
            longitude=longitude,
            geocode_source=geocode_source,
        )

    resolved = await asyncio.gather(*(resolve_session(session) for session in sessions))
    for point in resolved:
        if point is not None:
            points.append(point)
    return points


@router.get("/api/analytics", response_model=AnalyticsResponse)
async def analytics(
    organization_id: str | None = None,
    context: AuthContext = Depends(require_session),
):
    target_org = _target_org(context, organization_id)
    data = await get_analytics(target_org)
    return AnalyticsResponse(**data)


@router.get("/api/events")
async def events(
    count: int = 50,
    organization_id: str | None = None,
    context: AuthContext = Depends(require_session),
):
    target_org = _target_org(context, organization_id)
    return await get_events(count, target_org)


@router.get("/api/sessions/{session_id}/history")
async def session_history(
    session_id: str,
    context: AuthContext = Depends(require_session),
):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not context.is_superadmin and session.get("organization_id") != context.organization_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if context.is_superadmin and context.organization_id and session.get("organization_id") != context.organization_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await get_history(session_id)


@router.get("/api/analytics/detailed")
async def analytics_detailed(
    organization_id: str | None = None,
    context: AuthContext = Depends(require_session),
):
    target_org = _target_org(context, organization_id)
    base = await get_analytics(target_org)
    funnel = await get_funnel_counts(target_org)
    daily_reviews = await get_daily_counts("review_submitted", 7, organization_id=target_org)
    daily_started = await get_daily_counts("review_started", 7, organization_id=target_org)
    sessions = await get_all_sessions(target_org)
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
async def redis_stats(
    organization_id: str | None = None,
    context: AuthContext = Depends(require_session),
):
    target_org = _target_org(context, organization_id)
    return await get_redis_stats(target_org)


@router.get("/api/notifications")
async def notifications(
    request: Request,
    context: AuthContext = Depends(require_session),
):
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
                    payload = json.loads(message["data"])
                    if context.is_superadmin:
                        if context.organization_id and payload.get("organization_id") != context.organization_id:
                            continue
                    elif payload.get("organization_id") != context.organization_id:
                        continue
                    yield {"event": "notification", "data": json.dumps(payload)}
                else:
                    yield {"event": "ping", "data": ""}
                    await asyncio.sleep(2)
        finally:
            await pubsub.unsubscribe("plumber:notifications")
            await pubsub.aclose()

    return EventSourceResponse(event_stream())
