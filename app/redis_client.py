"""
Redis client — the centerpiece of Plumbly.

Uses 7 distinct Redis data structures / features:
1. JSON          — session state (Redis 8 built-in)
2. Lists         — ordered conversation history
3. Streams       — durable event pipeline
4. Pub/Sub       — real-time dashboard notifications
5. Sorted Sets   — analytics (reviews per day)
6. Vector Sets   — FAQ semantic search (Redis 8 native)
7. Key Expiry    — rate limiting via SET NX EX
"""

import json
import time
import uuid
from datetime import datetime, timezone

import numpy as np
import redis.asyncio as redis

from app.config import settings

pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global pool
    if pool is None:
        pool = redis.from_url(
            settings.redis_url, decode_responses=True, protocol=3
        )
    return pool


async def close_redis():
    global pool
    if pool:
        await pool.aclose()
        pool = None


# ---------------------------------------------------------------------------
# 1. JSON — Session State
# ---------------------------------------------------------------------------

async def create_session(
    customer_name: str,
    customer_phone: str = "",
    customer_email: str = "",
    customer_address: str = "",
    customer_zip: str = "",
    referral_source: str = "",
    job_description: str = "",
    job_type: str = "",
    job_total: str = "",
    job_date: str = "",
    plumber_name: str = "",
    is_repeat_customer: bool = False,
    follow_up_notes: str = "",
) -> str:
    r = await get_redis()
    session_id = str(uuid.uuid4())[:8]
    session_data = {
        "session_id": session_id,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "customer_email": customer_email,
        "customer_address": customer_address,
        "customer_zip": customer_zip,
        "referral_source": referral_source,
        "job_description": job_description,
        "job_type": job_type,
        "job_total": job_total,
        "job_date": job_date,
        "plumber_name": plumber_name,
        "is_repeat_customer": is_repeat_customer,
        "follow_up_notes": follow_up_notes,
        "device_type": "unknown",
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "message_count": 0,
    }
    await r.json().set(f"session:{session_id}", "$", session_data)
    await r.expire(f"session:{session_id}", settings.session_ttl)

    await emit_event(session_id, "job_completed", {
        "customer_name": customer_name,
        "plumber_name": plumber_name,
    })
    return session_id


async def get_session(session_id: str) -> dict | None:
    r = await get_redis()
    data = await r.json().get(f"session:{session_id}")
    return data


async def update_session(session_id: str, **fields):
    r = await get_redis()
    for key, value in fields.items():
        await r.json().set(f"session:{session_id}", f"$.{key}", value)


async def get_all_sessions() -> list[dict]:
    r = await get_redis()
    keys = []
    async for key in r.scan_iter("session:*"):
        keys.append(key)
    sessions = []
    for key in keys:
        data = await r.json().get(key)
        if data:
            sessions.append(data)
    return sessions


# ---------------------------------------------------------------------------
# 2. Lists — Conversation History
# ---------------------------------------------------------------------------

async def add_message(session_id: str, role: str, content: str):
    r = await get_redis()
    msg = json.dumps({"role": role, "content": content, "ts": time.time()})
    await r.rpush(f"chat:{session_id}", msg)
    await r.expire(f"chat:{session_id}", settings.session_ttl)
    await r.json().numincrby(f"session:{session_id}", "$.message_count", 1)


async def get_history(session_id: str) -> list[dict]:
    r = await get_redis()
    raw = await r.lrange(f"chat:{session_id}", 0, -1)
    return [json.loads(m) for m in raw]


# ---------------------------------------------------------------------------
# 3. Streams — Event Pipeline
# ---------------------------------------------------------------------------

async def emit_event(session_id: str, event_type: str, data: dict | None = None):
    r = await get_redis()
    entry = {
        "session_id": session_id,
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": json.dumps(data or {}),
    }
    await r.xadd("events:pipeline", entry)


async def get_events(count: int = 50) -> list[dict]:
    r = await get_redis()
    entries = await r.xrevrange("events:pipeline", count=count)
    results = []
    for entry_id, fields in entries:
        fields["id"] = entry_id
        if "data" in fields:
            fields["data"] = json.loads(fields["data"])
        results.append(fields)
    return results


# ---------------------------------------------------------------------------
# 4. Pub/Sub — Real-time Dashboard Notifications
# ---------------------------------------------------------------------------

async def publish_notification(channel: str, message: dict):
    r = await get_redis()
    await r.publish(channel, json.dumps(message))


async def subscribe_notifications(channel: str = "plumber:notifications"):
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    return pubsub


# ---------------------------------------------------------------------------
# 5. Sorted Sets — Analytics
# ---------------------------------------------------------------------------

async def track_review_event(event_type: str):
    r = await get_redis()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    await r.zincrby(f"analytics:{event_type}", 1, today)


async def get_daily_counts(event_type: str, days: int = 7) -> dict[str, int]:
    r = await get_redis()
    results = {}
    now = datetime.now(timezone.utc)
    for i in range(days):
        from datetime import timedelta
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        score = await r.zscore(f"analytics:{event_type}", day)
        results[day] = int(score) if score else 0
    return results


async def get_analytics() -> dict:
    r = await get_redis()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    reviews_today_score = await r.zscore("analytics:review_submitted", today)
    reviews_today = int(reviews_today_score) if reviews_today_score else 0

    reviews_week = await get_daily_counts("review_submitted", 7)

    sessions = await get_all_sessions()
    total = len(sessions)
    completed = sum(1 for s in sessions if s.get("status") == "submitted")
    rate = (completed / total * 100) if total > 0 else 0.0

    return {
        "reviews_today": reviews_today,
        "reviews_this_week": reviews_week,
        "total_sessions": total,
        "completion_rate": round(rate, 1),
    }


# ---------------------------------------------------------------------------
# 6. Vector Sets — FAQ Semantic Search (Redis 8 native)
# ---------------------------------------------------------------------------

FAQ_ENTRIES = [
    {
        "q": "I don't have a Google account",
        "a": "No worries! You can create a free Google account in about 2 minutes. Go to accounts.google.com and tap 'Create account'. You just need an email address to get started. Or if you have a Gmail, you already have a Google account!",
    },
    {
        "q": "Where do I tap to leave a review?",
        "a": "Once you open the review link, you'll see a star rating area. Tap the number of stars you'd like to give (5 stars would be amazing! ⭐), then you'll see a text box where you can write about your experience.",
    },
    {
        "q": "What should I write in the review?",
        "a": "Just share your honest experience! Some ideas: mention what work was done, how the plumber was (professional, on time, friendly), and whether you'd recommend us. Even a sentence or two helps a lot!",
    },
    {
        "q": "The link isn't working",
        "a": "Try opening the link in your default browser (Chrome on Android, Safari on iPhone). If it still doesn't work, you can search for our business name directly on Google Maps and leave the review from there.",
    },
    {
        "q": "Can I leave a review later?",
        "a": "Absolutely! The link will work anytime. But it's easiest to do it now while the experience is fresh — it only takes about 60 seconds!",
    },
    {
        "q": "Do I need to download an app?",
        "a": "Nope! You can leave a Google review right from your web browser. No app download needed. If you have the Google Maps app installed, the link might open there, which works great too.",
    },
    {
        "q": "Is my review anonymous?",
        "a": "Google reviews are posted under your Google account name. They're public, but you don't have to share any private details — just your experience with our service.",
    },
    {
        "q": "How long does it take?",
        "a": "Usually about 60 seconds! Just tap the stars and write a quick sentence. Easy peasy!",
    },
]


def _simple_embed(text: str, dim: int = 64) -> list[float]:
    """Deterministic lightweight text embedding using character n-gram hashing.

    Not a learned model — good enough for FAQ matching on short phrases.
    """
    vec = np.zeros(dim, dtype=np.float32)
    text_lower = text.lower()
    for n in (2, 3, 4):
        for i in range(len(text_lower) - n + 1):
            ngram = text_lower[i : i + n]
            h = hash(ngram) % dim
            vec[h] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


async def seed_faq_vectors():
    """Seed FAQ vectors into a Redis Vector Set (VADD — Redis 8 native)."""
    r = await get_redis()
    try:
        for i, entry in enumerate(FAQ_ENTRIES):
            embedding = _simple_embed(entry["q"])
            values_str = ",".join(str(v) for v in embedding)
            # VADD key [REDUCE dim] FP32 element val [val ...]
            await r.execute_command(
                "VADD", "faq:vectors", f"FP32:{len(embedding)}", f"faq:{i}",
                f"VALUES {len(embedding)} {values_str}",
            )
    except Exception:
        # Vector Sets might not be available (Redis < 8.0 or not compiled in).
        # Fall back to storing FAQs as a simple hash for keyword matching.
        for i, entry in enumerate(FAQ_ENTRIES):
            await r.hset("faq:fallback", f"faq:{i}", json.dumps(entry))


async def search_faq(question: str, top_k: int = 2) -> list[dict]:
    """Search FAQ using Redis Vector Sets (VSIM) or fallback to keyword matching."""
    r = await get_redis()
    try:
        embedding = _simple_embed(question)
        values_str = ",".join(str(v) for v in embedding)
        results = await r.execute_command(
            "VSIM", "faq:vectors", f"VALUES {len(embedding)} {values_str}",
            "COUNT", top_k,
        )
        matched = []
        for element in results:
            idx = int(element.split(":")[1]) if isinstance(element, str) else 0
            if 0 <= idx < len(FAQ_ENTRIES):
                matched.append(FAQ_ENTRIES[idx])
        return matched if matched else _keyword_fallback(question)
    except Exception:
        return _keyword_fallback(question)


def _keyword_fallback(question: str) -> list[dict]:
    """Simple keyword overlap matching as fallback."""
    q_words = set(question.lower().split())
    scored = []
    for entry in FAQ_ENTRIES:
        faq_words = set(entry["q"].lower().split())
        overlap = len(q_words & faq_words)
        if overlap > 0:
            scored.append((overlap, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:2]]


# ---------------------------------------------------------------------------
# 7. Key Expiry — Rate Limiting
# ---------------------------------------------------------------------------

async def check_rate_limit(ip: str, endpoint: str) -> bool:
    """Returns True if the request is allowed, False if rate-limited."""
    r = await get_redis()
    key = f"ratelimit:{ip}:{endpoint}"
    current = await r.get(key)
    if current is not None and int(current) >= settings.rate_limit_max:
        return False
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, settings.rate_limit_window)
    await pipe.execute()
    return True


async def get_redis_stats() -> list[dict]:
    """Return live stats for each Redis data structure used — interview showpiece."""
    r = await get_redis()

    # 1. JSON — Sessions
    session_keys = [k async for k in r.scan_iter("session:*")]
    # 2. Lists — Chat histories
    chat_keys = [k async for k in r.scan_iter("chat:*")]
    # 3. Streams — Event pipeline
    try:
        pipeline_len = await r.xlen("events:pipeline")
    except Exception:
        pipeline_len = 0
    # 4. Pub/Sub — Notification channels
    try:
        channels = await r.pubsub_channels("plumber:*")
        pubsub_count = len(channels)
    except Exception:
        pubsub_count = 0
    # 5. Sorted Sets — Analytics
    analytics_keys = [k async for k in r.scan_iter("analytics:*")]
    # 6. Vector Sets — FAQ
    try:
        faq_count = await r.execute_command("VCARD", "faq:vectors")
    except Exception:
        try:
            faq_count = await r.hlen("faq:fallback")
        except Exception:
            faq_count = 0
    # 7. Key Expiry — Rate limiting
    ratelimit_keys = [k async for k in r.scan_iter("ratelimit:*")]

    return [
        {
            "name": "Sessions",
            "type": "JSON",
            "key_pattern": "session:{id}",
            "count": len(session_keys),
            "purpose": "Customer session state with TTL expiry",
        },
        {
            "name": "Chat History",
            "type": "List",
            "key_pattern": "chat:{id}",
            "count": len(chat_keys),
            "purpose": "Ordered conversation messages (RPUSH/LRANGE)",
        },
        {
            "name": "Event Pipeline",
            "type": "Stream",
            "key_pattern": "events:pipeline",
            "count": pipeline_len,
            "purpose": "Durable event log (XADD/XREVRANGE)",
        },
        {
            "name": "Notifications",
            "type": "Pub/Sub",
            "key_pattern": "plumber:*",
            "count": pubsub_count,
            "purpose": "Real-time dashboard push via SSE",
        },
        {
            "name": "Analytics",
            "type": "Sorted Set",
            "key_pattern": "analytics:{event}",
            "count": len(analytics_keys),
            "purpose": "Daily review counts (ZINCRBY/ZSCORE)",
        },
        {
            "name": "FAQ Vectors",
            "type": "Vector Set",
            "key_pattern": "faq:vectors",
            "count": faq_count,
            "purpose": "Semantic FAQ search (VADD/VSIM)",
        },
        {
            "name": "Rate Limits",
            "type": "Key Expiry",
            "key_pattern": "ratelimit:{ip}:{endpoint}",
            "count": len(ratelimit_keys),
            "purpose": "Spam prevention via SET NX EX",
        },
    ]


async def get_funnel_counts() -> dict[str, int]:
    """Count events by type from the pipeline stream for funnel visualization."""
    r = await get_redis()
    counts: dict[str, int] = {
        "job_completed": 0,
        "customer_contacted": 0,
        "review_started": 0,
        "review_submitted": 0,
    }
    try:
        entries = await r.xrange("events:pipeline")
        for _, fields in entries:
            event = fields.get("event", "")
            if event in counts:
                counts[event] += 1
    except Exception:
        pass
    return counts
