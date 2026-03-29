"""Provider-ready Twilio webhook endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse, Response
from twilio.twiml.messaging_response import MessagingResponse

from app.config import settings
from app.redis_client import (
    emit_event,
    find_session_by_sms_sid,
    get_sessions_by_phone,
    set_sms_opt_out,
    update_session,
)
from app.phone_utils import normalize_phone_number

router = APIRouter()

STOP_WORDS = {"STOP", "STOPALL", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"}
START_WORDS = {"START", "UNSTOP"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _twiml_message(message: str) -> Response:
    response = MessagingResponse()
    if message:
        response.message(message)
    return Response(content=str(response), media_type="application/xml")


@router.post("/webhooks/twilio/inbound")
async def twilio_inbound_webhook(
    From: str = Form(""),
    Body: str = Form(""),
    MessageSid: str = Form(""),
):
    normalized_phone = normalize_phone_number(From)
    command = (Body or "").strip().upper()
    sessions = await get_sessions_by_phone(normalized_phone)

    if command in STOP_WORDS:
        await set_sms_opt_out(
            normalized_phone,
            opted_out=True,
            source="twilio_inbound_stop",
            message_sid=MessageSid,
            body=Body,
        )
        for session in sessions:
            await update_session(
                session["session_id"],
                sms_opt_out=True,
                sms_delivery_status="opted_out",
                sms_status_updated_at=_now_iso(),
            )
            await emit_event(
                session["session_id"],
                "sms_opt_out",
                {"phone": normalized_phone, "message_sid": MessageSid},
                organization_id=session.get("organization_id"),
            )
        return _twiml_message(
            f"You've been unsubscribed from {settings.business_name} review texts. Reply START to resubscribe."
        )

    if command in START_WORDS:
        await set_sms_opt_out(
            normalized_phone,
            opted_out=False,
            source="twilio_inbound_start",
            message_sid=MessageSid,
            body=Body,
        )
        for session in sessions:
            await update_session(
                session["session_id"],
                sms_opt_out=False,
                sms_status_updated_at=_now_iso(),
            )
            await emit_event(
                session["session_id"],
                "sms_resubscribed",
                {"phone": normalized_phone, "message_sid": MessageSid},
                organization_id=session.get("organization_id"),
            )
        return _twiml_message(
            f"You're resubscribed to {settings.business_name} review texts."
        )

    if command == "HELP":
        return _twiml_message(
            f"{settings.business_name}: reply STOP to opt out. For help, contact support."
        )

    return _twiml_message("")


@router.post("/webhooks/twilio/status")
async def twilio_status_webhook(
    MessageSid: str = Form(""),
    MessageStatus: str = Form(""),
    To: str = Form(""),
    ErrorCode: str = Form(""),
    ErrorMessage: str = Form(""),
):
    session = await find_session_by_sms_sid(MessageSid)
    if session is None:
        matches = await get_sessions_by_phone(To)
        session = matches[0] if matches else None

    if session is not None:
        await update_session(
            session["session_id"],
            sms_message_sid=MessageSid or session.get("sms_message_sid", ""),
            sms_delivery_status=MessageStatus or "unknown",
            sms_error=ErrorMessage or "",
            sms_error_code=ErrorCode or "",
            sms_status_updated_at=_now_iso(),
        )
        await emit_event(
            session["session_id"],
            f"sms_{(MessageStatus or 'unknown').lower()}",
            {
                "message_sid": MessageSid,
                "status": MessageStatus,
                "error_code": ErrorCode,
                "error_message": ErrorMessage,
            },
            organization_id=session.get("organization_id"),
        )

    return JSONResponse({"ok": True})
