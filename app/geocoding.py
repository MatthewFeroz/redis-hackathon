"""
Geocoding helpers for the customer map.

Uses Redis for caching and Nominatim as a best-effort geocoder. When only ZIP
code data is available, the returned point is an approximate area centroid.
"""

import asyncio
import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.config import settings
from app.redis_client import get_redis


def _normalize_part(value: str) -> str:
    return " ".join(value.strip().lower().split())


def build_geocode_query(address: str, zip_code: str) -> str:
    parts = [_normalize_part(address), _normalize_part(zip_code)]
    return ", ".join(part for part in parts if part)


async def get_cached_geocode(query: str) -> dict[str, Any] | None:
    if not query:
        return None
    r = await get_redis()
    raw = await r.get(f"geocode:{query}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def cache_geocode(query: str, payload: dict[str, Any], ttl_seconds: int = 86400 * 30) -> None:
    if not query:
        return
    r = await get_redis()
    await r.set(f"geocode:{query}", json.dumps(payload), ex=ttl_seconds)


def _request_geocode(query: str) -> dict[str, Any] | None:
    params = urlencode(
        {
            "q": query,
            "format": "jsonv2",
            "limit": 1,
            "countrycodes": "us",
            "addressdetails": 0,
        }
    )
    req = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": settings.geocoding_user_agent},
    )
    with urlopen(req, timeout=settings.geocoding_timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload:
        return None
    match = payload[0]
    return {
        "latitude": float(match["lat"]),
        "longitude": float(match["lon"]),
        "display_name": match.get("display_name", ""),
        "geocode_source": "nominatim",
    }


async def geocode_location(address: str, zip_code: str) -> dict[str, Any] | None:
    query = build_geocode_query(address, zip_code)
    if not query:
        return None

    cached = await get_cached_geocode(query)
    if cached is not None:
        return cached

    try:
        payload = await asyncio.to_thread(_request_geocode, query)
    except Exception:
        payload = None

    if payload is None and address and zip_code:
        try:
            payload = await asyncio.to_thread(_request_geocode, zip_code)
        except Exception:
            payload = None
        if payload is not None:
            payload["geocode_source"] = "zip_fallback"

    if payload is None:
        payload = {"geocode_error": "not_found"}

    await cache_geocode(query, payload)
    return payload
