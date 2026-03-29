"""
Twilio SMS integration — sends review links to customers.
"""

from twilio.rest import Client

from app.config import settings
from app.phone_utils import normalize_phone_number


def _get_client() -> Client | None:
    if (
        not settings.twilio_account_sid
        or not settings.twilio_auth_token
        or not settings.twilio_messaging_service_sid
    ):
        return None
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)


async def send_review_link(
    to_phone: str,
    customer_name: str,
    review_link: str,
    plumber_name: str = "",
) -> dict:
    """Send an SMS with the review link. Returns message SID or error."""
    client = _get_client()
    if not client:
        return {"sent": False, "error": "Twilio not configured"}

    if not to_phone:
        return {"sent": False, "error": "No phone number provided"}

    phone = normalize_phone_number(to_phone)

    plumber_line = f" {plumber_name} at" if plumber_name else ""
    body = (
        f"Hi {customer_name}! Thanks for choosing{plumber_line} "
        f"{settings.business_name}. "
        f"We'd really appreciate a quick Google review — it only takes 60 seconds!\n\n"
        f"{review_link}"
    )

    try:
        message = client.messages.create(
            to=phone,
            messaging_service_sid=settings.twilio_messaging_service_sid,
            body=body,
        )
        return {
            "sent": True,
            "sid": message.sid,
            "status": getattr(message, "status", "") or "queued",
            "normalized_phone": phone,
        }
    except Exception as e:
        return {"sent": False, "error": str(e), "normalized_phone": phone}
