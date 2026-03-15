"""
Customer-facing routes: chat page, API endpoints.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.agent import chat, get_initial_greeting
from app.models import ChatRequest, ChatResponse
from app.redis_client import check_rate_limit, get_session

router = APIRouter()


@router.get("/review/{session_id}", response_class=HTMLResponse)
async def review_page(session_id: str, request: Request):
    session = await get_session(session_id)
    if not session:
        return HTMLResponse(
            "<h1>Link expired or invalid</h1><p>Please contact us for a new review link.</p>",
            status_code=404,
        )
    with open("static/chat.html") as f:
        html = f.read()
    html = html.replace("{{SESSION_ID}}", session_id)
    html = html.replace("{{CUSTOMER_NAME}}", session.get("customer_name", ""))
    return HTMLResponse(html)


@router.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/api/greeting/{session_id}")
async def greeting(session_id: str, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit(client_ip, "greeting"):
        raise HTTPException(status_code=429, detail="Too many requests")
    try:
        text = await get_initial_greeting(session_id)
        return {"reply": text, "session_id": session_id}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not await check_rate_limit(client_ip, "chat"):
        raise HTTPException(status_code=429, detail="Too many requests")

    session = await get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    reply = await chat(body.session_id, body.message, body.device_type)

    updated = await get_session(body.session_id)
    return ChatResponse(
        reply=reply,
        session_id=body.session_id,
        status=updated.get("status", "unknown") if updated else "unknown",
    )
