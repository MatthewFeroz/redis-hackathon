"""
Plumber-facing routes: dashboard, job creation, analytics, SSE notifications.
"""

import asyncio
import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from sse_starlette.sse import EventSourceResponse

from app.auth import AuthContext, require_role, require_session
from app.config import settings
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
BUILD_DIR = Path("dashboard-app") / "build"


def _target_org(context: AuthContext, requested: str | None) -> str | None:
    if context.is_superadmin:
        if requested in (None, "", "all"):
            return context.organization_id
        return requested
    return context.organization_id


def _load_dashboard_html() -> HTMLResponse:
    build_index = os.path.join("dashboard-app", "build", "index.html")
    if os.path.exists(build_index):
        with open(build_index) as f:
            return HTMLResponse(f.read())
    with open("static/dashboard.html") as f:
        return HTMLResponse(f.read())


@router.get("/", response_class=HTMLResponse)
async def dashboard_page():
    return _load_dashboard_html()


@router.get("/sms-consent", response_class=HTMLResponse)
async def sms_consent_page():
    business_name = settings.business_name or "Alive Plumbing"
    support_email = "alivecompanybusiness@gmail.com"
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{business_name} SMS Consent Disclosure</title>
        <style>
          :root {{
            color-scheme: light;
            --bg: #f6f7f9;
            --panel: #ffffff;
            --text: #101828;
            --muted: #475467;
            --border: #d0d5dd;
            --accent: #1570ef;
          }}
          * {{ box-sizing: border-box; }}
          body {{
            margin: 0;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(180deg, #eef4ff 0%, var(--bg) 40%);
            color: var(--text);
            line-height: 1.6;
          }}
          main {{
            max-width: 860px;
            margin: 0 auto;
            padding: 48px 20px 72px;
          }}
          section {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 24px;
            margin-top: 18px;
            box-shadow: 0 8px 30px rgba(16, 24, 40, 0.05);
          }}
          h1, h2 {{ line-height: 1.2; }}
          h1 {{ font-size: 2rem; margin: 0 0 12px; }}
          h2 {{ font-size: 1.1rem; margin: 0 0 12px; }}
          p, li {{ color: var(--muted); }}
          code, pre {{
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 12px;
          }}
          pre {{
            padding: 14px;
            white-space: pre-wrap;
          }}
          .eyebrow {{
            display: inline-block;
            font-size: 0.8rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--accent);
            font-weight: 700;
            margin-bottom: 10px;
          }}
          .grid {{
            display: grid;
            gap: 18px;
          }}
          @media (min-width: 768px) {{
            .grid {{
              grid-template-columns: 1fr 1fr;
            }}
          }}
          a {{ color: var(--accent); }}
        </style>
      </head>
      <body>
        <main>
          <span class="eyebrow">Public Compliance Page</span>
          <h1>{business_name} SMS Consent Disclosure</h1>
          <p>
            This page documents the verbal opt-in workflow used before sending a single
            customer-care review request text after a completed plumbing service visit.
          </p>

          <section>
            <h2>Messaging Use Case</h2>
            <p>
              Customers receive one customer-care text message after a completed service
              appointment. The message contains a personalized review link and does not
              include promotional or marketing content.
            </p>
            <pre>Hi {{customer_name}}, thanks for choosing {business_name} today. Here is your review link: {{review_link}}. Reply STOP to opt out.</pre>
          </section>

          <section>
            <h2>Verbal Consent Script</h2>
            <p>Staff must read the following script before any text message is sent:</p>
            <pre>"Would it be okay if we send you one text message with your review link for today's service? Message and data rates may apply. Reply STOP to opt out."</pre>
            <p>
              The customer must verbally answer "yes" before any text message is sent.
              If the customer declines, no message is sent.
            </p>
          </section>

          <section>
            <h2>Simulated Verbal Opt-In Conversation</h2>
            <pre>
Technician: Would it be okay if we send you one text message with your review link for today's service? Message and data rates may apply. Reply STOP to opt out.

Customer: Yes, that's fine.

Technician: Great, we'll send one customer-care message to the phone number on this work order. You can reply STOP at any time to opt out.
            </pre>
          </section>

          <section>
            <h2>How Consent Is Recorded</h2>
            <div class="grid">
              <div>
                <p>We record the following details when verbal consent is collected:</p>
                <ul>
                  <li>Customer full name</li>
                  <li>Customer mobile number</li>
                  <li>Date and time of consent</li>
                  <li>Staff member / technician who collected consent</li>
                  <li>Associated service job or work-order reference</li>
                </ul>
              </div>
              <div>
                <p>Internal controls:</p>
                <ul>
                  <li>Only one customer-care review request is sent per completed service visit</li>
                  <li>No message is sent without a "yes" response</li>
                  <li>Opt-out keywords are honored immediately</li>
                  <li>Consent records are retained with the service record</li>
                </ul>
              </div>
            </div>
          </section>

          <section>
            <h2>Opt-Out Instructions</h2>
            <p>
              Message recipients may opt out at any time by replying
              <strong>STOP</strong>. We also honor <strong>CANCEL</strong>,
              <strong>END</strong>, <strong>UNSUBSCRIBE</strong>, and
              <strong>QUIT</strong>.
            </p>
          </section>

          <section>
            <h2>Support Contact</h2>
            <p>
              For messaging support questions, contact
              <a href="mailto:{support_email}">{support_email}</a>.
            </p>
          </section>
        </main>
      </body>
    </html>
    """
    return HTMLResponse(html)


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy_page():
    business_name = settings.business_name or "Alive Plumbing"
    support_email = "alivecompanybusiness@gmail.com"
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{business_name} Privacy Policy</title>
        <style>
          body {{
            margin: 0;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f5f7fb;
            color: #101828;
            line-height: 1.65;
          }}
          main {{
            max-width: 860px;
            margin: 0 auto;
            padding: 48px 20px 72px;
          }}
          section {{
            background: #fff;
            border: 1px solid #d0d5dd;
            border-radius: 18px;
            padding: 24px;
            margin-top: 18px;
          }}
          h1, h2 {{ line-height: 1.2; }}
          h1 {{ margin-bottom: 12px; }}
          p, li {{ color: #475467; }}
          a {{ color: #1570ef; }}
        </style>
      </head>
      <body>
        <main>
          <h1>{business_name} Privacy Policy</h1>
          <p>
            This Privacy Policy explains how {business_name} collects, uses, and protects
            personal information provided through our website and customer communication tools.
          </p>

          <section>
            <h2>Information We Collect</h2>
            <ul>
              <li>Name, phone number, email address, and service address</li>
              <li>Work-order and service visit information</li>
              <li>Consent records related to customer communications</li>
              <li>Review interaction and support communication records</li>
            </ul>
          </section>

          <section>
            <h2>How We Use Information</h2>
            <ul>
              <li>Provide and manage plumbing services</li>
              <li>Send customer-care messages related to completed services</li>
              <li>Send review links after consent has been collected</li>
              <li>Respond to support requests and maintain service records</li>
            </ul>
          </section>

          <section>
            <h2>SMS Messaging</h2>
            <p>
              SMS consent is not shared with third parties or affiliates for marketing purposes.
              We only send customer-care messages after consent is collected.
              Recipients may reply STOP to opt out or HELP for support.
            </p>
          </section>

          <section>
            <h2>Data Sharing</h2>
            <p>
              We may use service providers to help operate our business, including hosting,
              analytics, messaging, and customer support tools. We do not sell personal
              information.
            </p>
          </section>

          <section>
            <h2>Contact</h2>
            <p>
              For privacy questions, contact
              <a href="mailto:{support_email}">{support_email}</a>.
            </p>
          </section>
        </main>
      </body>
    </html>
    """
    return HTMLResponse(html)


@router.get("/terms", response_class=HTMLResponse)
async def terms_page():
    business_name = settings.business_name or "Alive Plumbing"
    support_email = "alivecompanybusiness@gmail.com"
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{business_name} Terms & Conditions</title>
        <style>
          body {{
            margin: 0;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f5f7fb;
            color: #101828;
            line-height: 1.65;
          }}
          main {{
            max-width: 860px;
            margin: 0 auto;
            padding: 48px 20px 72px;
          }}
          section {{
            background: #fff;
            border: 1px solid #d0d5dd;
            border-radius: 18px;
            padding: 24px;
            margin-top: 18px;
          }}
          h1, h2 {{ line-height: 1.2; }}
          h1 {{ margin-bottom: 12px; }}
          p, li {{ color: #475467; }}
          a {{ color: #1570ef; }}
        </style>
      </head>
      <body>
        <main>
          <h1>{business_name} Terms & Conditions</h1>
          <p>
            These Terms & Conditions govern the use of our website, customer communication
            tools, and SMS messaging related to completed plumbing services.
          </p>

          <section>
            <h2>SMS Program Description</h2>
            <p>
              Customers may receive one customer-care SMS after a completed service visit
              containing a personalized review link. Message frequency varies by service
              activity but is limited to customer-care use only for this workflow.
            </p>
          </section>

          <section>
            <h2>Consent and Opt-Out</h2>
            <p>
              Customers must provide consent before receiving SMS messages. Message and data
              rates may apply. Reply STOP to opt out at any time. Reply HELP for support.
            </p>
          </section>

          <section>
            <h2>Support</h2>
            <p>
              For support regarding this messaging program, contact
              <a href="mailto:{support_email}">{support_email}</a>.
            </p>
          </section>

          <section>
            <h2>General Terms</h2>
            <p>
              We may update these terms from time to time. Continued use of our services
              constitutes acceptance of the updated terms.
            </p>
          </section>
        </main>
      </body>
    </html>
    """
    return HTMLResponse(html)


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


@router.get("/{frontend_path:path}", response_class=HTMLResponse)
async def frontend_route(frontend_path: str):
    candidate = (BUILD_DIR / frontend_path).resolve()
    build_root = BUILD_DIR.resolve()

    # Serve built frontend assets like /favicon.svg and /brand-star.svg
    # before falling back to the SPA shell.
    if build_root in candidate.parents and candidate.is_file():
        return FileResponse(candidate)

    if (
        frontend_path.startswith("api/")
        or frontend_path.startswith("auth/")
        or frontend_path.startswith("review/")
        or frontend_path.startswith("_app/")
        or frontend_path.startswith("static/")
        or frontend_path == "health"
    ):
        raise HTTPException(status_code=404, detail="Not Found")
    return _load_dashboard_html()
