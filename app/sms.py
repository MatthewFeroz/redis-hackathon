"""
Twilio SMS integration — sends review links to customers.
"""

from twilio.rest import Client

from app.config import settings


def _get_client() -> Client | None:
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
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

    # Normalize phone: add +1 if it looks like a US number without country code
    phone = to_phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not phone.startswith("+"):
        if phone.startswith("1") and len(phone) == 11:
            phone = f"+{phone}"
        elif len(phone) == 10:
            phone = f"+1{phone}"
        else:
            phone = f"+{phone}"

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
        return {"sent": True, "sid": message.sid}
    except Exception as e:
        return {"sent": False, "error": str(e)}
