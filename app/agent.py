"""
Gemini agent — system prompt, chat, and status detection.
"""

import re

from google import genai

from app.config import settings
from app.redis_client import (
    add_message,
    emit_event,
    get_history,
    get_session,
    publish_notification,
    search_faq,
    track_review_event,
    update_session,
)

client = genai.Client(api_key=settings.gemini_api_key)
MODEL = "gemini-2.5-flash"


def build_system_prompt(session: dict) -> str:
    faq_context = ""  # populated per-turn if relevant
    return f"""You are a friendly, helpful review assistant for {settings.business_name}.

CONTEXT:
- Customer name: {session.get('customer_name', 'there')}
- Plumber who did the job: {session.get('plumber_name', 'our plumber')}
- Job description: {session.get('job_description', 'plumbing service')}
- Customer's device: {session.get('device_type', 'unknown')}
- Google Review link: {settings.google_review_url}

YOUR GOAL:
Walk the customer through leaving a Google review. Be warm, conversational, and helpful.
Keep messages SHORT (2-3 sentences max). You're texting, not writing an essay.

FLOW:
1. Greet them warmly, mention the plumber by name and the job done
2. Ask if they'd be willing to leave a quick Google review (takes ~60 seconds)
3. Share the review link: {settings.google_review_url}
4. Give device-specific instructions based on their device type:
   - iPhone: "Tap the link → it'll open in Safari → tap the stars → write a quick note → tap Post"
   - Android: "Tap the link → it'll open in Chrome or Google Maps → tap the stars → write a quick note → tap Post"
   - Desktop: "Click the link → sign into Google if needed → click the stars → write a review → click Post"
5. Answer any questions they have (account issues, where to tap, what to write)
6. Thank them warmly when they say they've posted it

RULES:
- Never be pushy. If they decline, thank them for their time.
- If they ask something you can't answer, be honest.
- Don't repeat instructions they've already seen.
- Use casual, friendly language. No corporate speak.
- If they seem confused, simplify and offer to help step by step.
{faq_context}"""


# Status keywords that indicate progress
STATUS_PATTERNS = {
    "submitted": [
        r"\b(done|posted|submitted|left .* review|wrote .* review|finished|completed)\b",
        r"\b(just (left|posted|wrote|submitted))\b",
        r"\bgave .* stars?\b",
    ],
    "declined": [
        r"\b(no thanks|not interested|don't want|can't|won't|rather not|pass)\b",
        r"\bmaybe later\b",
    ],
    "needs_help": [
        r"\b(help|confused|don't understand|stuck|can't find|where|how do i)\b",
        r"\bdoesn't work\b",
        r"\bnot working\b",
    ],
}


def detect_status(message: str) -> str | None:
    lower = message.lower()
    for status, patterns in STATUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lower):
                return status
    return None


async def chat(session_id: str, user_message: str, device_type: str = "unknown") -> str:
    session = await get_session(session_id)
    if not session:
        return "Sorry, I couldn't find your session. Please check your link and try again."

    if device_type != "unknown" and session.get("device_type") == "unknown":
        await update_session(session_id, device_type=device_type)
        session["device_type"] = device_type

    # Update status on first real message
    if session.get("status") == "created":
        await update_session(session_id, status="contacted")
        await emit_event(session_id, "customer_contacted")
        await track_review_event("sessions_started")

    # Check for FAQ-matchable questions
    faq_matches = await search_faq(user_message)
    faq_context = ""
    if faq_matches:
        faq_context = "\n\nRELEVANT FAQ (use naturally if applicable):\n"
        for faq in faq_matches:
            faq_context += f"Q: {faq['q']}\nA: {faq['a']}\n\n"

    # Detect status changes
    detected = detect_status(user_message)
    if detected == "submitted":
        await update_session(session_id, status="submitted")
        await emit_event(session_id, "review_submitted", {
            "customer_name": session.get("customer_name", ""),
        })
        await track_review_event("review_submitted")
        await publish_notification("plumber:notifications", {
            "type": "review_submitted",
            "customer_name": session.get("customer_name", ""),
            "session_id": session_id,
        })
    elif detected == "declined":
        await update_session(session_id, status="declined")
        await emit_event(session_id, "review_declined")
    elif detected == "needs_help" and session.get("status") != "submitted":
        await update_session(session_id, status="needs_help")

    # Build conversation history for Gemini
    history = await get_history(session_id)
    system_prompt = build_system_prompt(session)
    if faq_context:
        system_prompt += faq_context

    contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=contents,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=2048,
        ),
    )

    reply = response.text or "I'm sorry, I had trouble generating a response. Could you try again?"

    # Ensure the review link is included in early replies when the customer
    # is agreeing or asking how to leave a review (first few messages)
    review_url = settings.google_review_url
    if (
        review_url
        and review_url not in reply
        and len(history) <= 4
        and session.get("status") not in ("submitted", "declined")
        and not any(review_url in m.get("content", "") for m in history)
    ):
        reply += f"\n\nHere's the link: {review_url}"

    # Store messages
    await add_message(session_id, "user", user_message)
    await add_message(session_id, "assistant", reply)

    return reply


async def get_initial_greeting(session_id: str) -> str:
    """Generate the first greeting when a customer opens the chat."""
    session = await get_session(session_id)
    if not session:
        return "Hi there! It looks like this link may have expired. Please contact us for a new one."

    system_prompt = build_system_prompt(session)
    prompt = (
        f"The customer just opened the chat link. Send a warm, short greeting. "
        f"Mention {session.get('plumber_name', 'our plumber')} by name and the "
        f"job ({session.get('job_description', 'recent service')}). "
        f"Ask if they'd be willing to leave a quick Google review."
    )

    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=2048,
        ),
    )

    greeting = response.text or (
        f"Hi {session.get('customer_name', 'there')}! Thanks for choosing "
        f"{settings.business_name}. Would you mind leaving us a quick Google review? "
        f"It only takes about 60 seconds! 😊"
    )

    await add_message(session_id, "assistant", greeting)
    await update_session(session_id, status="contacted")
    await emit_event(session_id, "customer_contacted")
    await track_review_event("sessions_started")

    return greeting
