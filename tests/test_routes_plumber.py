"""Tests for plumber dashboard routes."""

import pytest
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app():
    """Import app with redis lifespan disabled."""
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    import app.main as main_mod

    main_mod.app.router.lifespan_context = noop_lifespan
    return main_mod.app


@pytest.mark.asyncio
async def test_customer_map_points_geocodes_and_persists(app):
    sessions = [
        {
            "session_id": "abc12345",
            "customer_name": "Ada Lovelace",
            "customer_address": "123 Main St",
            "customer_zip": "10001",
            "status": "contacted",
            "latitude": None,
            "longitude": None,
            "geocode_source": "",
        }
    ]

    with patch("app.routes_plumber.get_all_sessions", new_callable=AsyncMock, return_value=sessions), \
         patch(
             "app.routes_plumber.geocode_location",
             new_callable=AsyncMock,
             return_value={"latitude": 40.7506, "longitude": -73.9972, "geocode_source": "nominatim"},
         ), \
         patch("app.routes_plumber.update_session", new_callable=AsyncMock) as mock_update:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/api/customers/map")

    assert resp.status_code == 200
    data = resp.json()
    assert data == [
        {
            "session_id": "abc12345",
            "customer_name": "Ada Lovelace",
            "customer_address": "123 Main St",
            "customer_zip": "10001",
            "status": "contacted",
            "latitude": 40.7506,
            "longitude": -73.9972,
            "geocode_source": "nominatim",
        }
    ]
    mock_update.assert_awaited_once()


@pytest.mark.asyncio
async def test_customer_map_points_skips_unresolvable_sessions(app):
    sessions = [
        {
            "session_id": "bad12345",
            "customer_name": "Unknown",
            "customer_address": "",
            "customer_zip": "00000",
            "status": "created",
            "latitude": None,
            "longitude": None,
            "geocode_source": "",
        }
    ]

    with patch("app.routes_plumber.get_all_sessions", new_callable=AsyncMock, return_value=sessions), \
         patch(
             "app.routes_plumber.geocode_location",
             new_callable=AsyncMock,
             return_value={"geocode_error": "not_found"},
         ), \
         patch("app.routes_plumber.update_session", new_callable=AsyncMock) as mock_update:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/api/customers/map")

    assert resp.status_code == 200
    assert resp.json() == []
    mock_update.assert_awaited_once()
