"""
Authentication and authorization helpers for WorkOS-backed dashboard access.
"""

import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

from fastapi import HTTPException, Request, Response, status
from workos import WorkOSClient

from app.config import settings
from app.redis_client import get_redis


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "organization"


def _normalize_role(role: str | None) -> str:
    normalized = (role or "member").lower()
    if normalized in {"owner", "admin", "member"}:
        return normalized
    return "member"


@dataclass
class AuthContext:
    session_id: str
    workos_session_id: str
    user_id: str
    email: str
    first_name: str | None
    last_name: str | None
    organization_id: str | None
    organization_name: str | None
    role: str
    platform_role: str | None
    is_superadmin: bool


def get_workos_client() -> WorkOSClient:
    if not settings.workos_api_key or not settings.workos_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WorkOS is not configured",
        )
    return WorkOSClient(
        api_key=settings.workos_api_key,
        client_id=settings.workos_client_id,
    )


async def create_auth_state(screen_hint: str, return_to: str) -> str:
    r = await get_redis()
    state = secrets.token_urlsafe(24)
    payload = {
        "screen_hint": screen_hint,
        "return_to": return_to,
        "created_at": _utcnow_iso(),
    }
    await r.set(f"auth_state:{state}", json.dumps(payload), ex=settings.auth_state_ttl)
    return state


async def consume_auth_state(state: str) -> dict[str, Any]:
    r = await get_redis()
    key = f"auth_state:{state}"
    data = await r.get(key)
    await r.delete(key)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid auth state")
    return json.loads(data)


async def get_user(user_id: str) -> dict[str, Any] | None:
    r = await get_redis()
    return await r.json().get(f"user:{user_id}")


async def get_org(organization_id: str) -> dict[str, Any] | None:
    r = await get_redis()
    return await r.json().get(f"org:{organization_id}")


async def list_orgs() -> list[dict[str, Any]]:
    r = await get_redis()
    orgs: list[dict[str, Any]] = []
    async for key in r.scan_iter("org:*"):
        data = await r.json().get(key)
        if data:
            orgs.append(data)
    orgs.sort(key=lambda org: org.get("name", "").lower())
    return orgs


async def list_memberships_for_user(user_id: str) -> list[dict[str, Any]]:
    r = await get_redis()
    organization_ids = await r.smembers(f"user_orgs:{user_id}")
    memberships: list[dict[str, Any]] = []
    for organization_id in sorted(organization_ids):
        data = await r.json().get(f"membership:{organization_id}:{user_id}")
        if data:
            memberships.append(data)
    return memberships


async def upsert_identity(auth_response) -> dict[str, Any]:
    r = await get_redis()
    user = auth_response.user
    membership_resource = get_workos_client().user_management.list_organization_memberships(
        user_id=user.id,
        statuses=["active"],
        limit=100,
    )
    memberships = membership_resource.data
    if not memberships:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No organization access",
        )

    selected_membership = None
    if auth_response.organization_id:
        selected_membership = next(
            (membership for membership in memberships if membership.organization_id == auth_response.organization_id),
            None,
        )
    if selected_membership is None:
        selected_membership = memberships[0]

    organization = get_workos_client().organizations.get_organization(
        selected_membership.organization_id
    )
    role = _normalize_role(selected_membership.role.get("slug"))
    platform_role = "superadmin" if user.email.lower() in settings.superadmin_email_set else None

    user_data = {
        "id": user.id,
        "workos_user_id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "organization_id": selected_membership.organization_id,
        "is_active": True,
        "platform_role": platform_role,
        "created_at": user.created_at,
        "last_login_at": user.last_sign_in_at or _utcnow_iso(),
    }
    await r.json().set(f"user:{user.id}", "$", user_data)

    org_data = {
        "id": organization.id,
        "workos_organization_id": organization.id,
        "name": organization.name,
        "slug": _slugify(organization.name),
        "created_at": organization.created_at,
    }
    await r.json().set(f"org:{organization.id}", "$", org_data)

    membership_data = {
        "user_id": user.id,
        "organization_id": selected_membership.organization_id,
        "role": role,
        "created_at": selected_membership.created_at,
        "updated_at": selected_membership.updated_at,
    }
    await r.json().set(
        f"membership:{selected_membership.organization_id}:{user.id}",
        "$",
        membership_data,
    )
    await r.sadd(f"org_users:{selected_membership.organization_id}", user.id)
    await r.sadd(f"user_orgs:{user.id}", selected_membership.organization_id)

    return {
        "user": user_data,
        "organization": org_data,
        "membership": membership_data,
        "platform_role": platform_role,
    }


async def create_app_session(
    *,
    sealed_session: str,
    workos_session_id: str,
    user_id: str,
    organization_id: str | None,
    role: str,
    platform_role: str | None,
) -> str:
    r = await get_redis()
    session_id = secrets.token_urlsafe(32)
    now = _utcnow_iso()
    session_data = {
        "session_id": session_id,
        "sealed_session": sealed_session,
        "workos_session_id": workos_session_id,
        "user_id": user_id,
        "organization_id": organization_id,
        "active_organization_id": organization_id,
        "role": role,
        "platform_role": platform_role,
        "created_at": now,
        "last_seen_at": now,
    }
    await r.json().set(f"auth_session:{session_id}", "$", session_data)
    await r.expire(f"auth_session:{session_id}", settings.auth_session_ttl)
    return session_id


async def get_app_session(session_id: str) -> dict[str, Any] | None:
    r = await get_redis()
    data = await r.json().get(f"auth_session:{session_id}")
    if data:
        await r.expire(f"auth_session:{session_id}", settings.auth_session_ttl)
        await r.json().set(
            f"auth_session:{session_id}",
            "$.last_seen_at",
            _utcnow_iso(),
        )
    return data


async def delete_app_session(session_id: str) -> None:
    r = await get_redis()
    await r.delete(f"auth_session:{session_id}")


async def set_active_organization(session_id: str, organization_id: str | None) -> None:
    r = await get_redis()
    await r.json().set(
        f"auth_session:{session_id}",
        "$.active_organization_id",
        organization_id,
    )
    await r.expire(f"auth_session:{session_id}", settings.auth_session_ttl)


def set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=settings.auth_session_cookie_name,
        value=session_id,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.auth_session_ttl,
        domain=settings.cookie_domain or None,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth_session_cookie_name,
        domain=settings.cookie_domain or None,
        path="/",
    )


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


async def require_session(request: Request) -> AuthContext:
    session_id = request.cookies.get(settings.auth_session_cookie_name)
    if not session_id:
        raise _unauthorized()

    app_session = await get_app_session(session_id)
    if not app_session:
        raise _unauthorized()

    workos_session = get_workos_client().user_management.load_sealed_session(
        sealed_session=app_session["sealed_session"],
        cookie_password=settings.workos_cookie_password,
    )
    auth_response = workos_session.authenticate()
    if not auth_response.authenticated:
        await delete_app_session(session_id)
        raise _unauthorized()

    user = await get_user(app_session["user_id"])
    if not user:
        await delete_app_session(session_id)
        raise _unauthorized()

    organization_id = app_session.get("active_organization_id")
    if organization_id is None and not app_session.get("platform_role"):
        organization_id = app_session.get("organization_id") or user.get("organization_id")
    org = await get_org(organization_id) if organization_id else None
    platform_role = app_session.get("platform_role")
    return AuthContext(
        session_id=session_id,
        workos_session_id=auth_response.session_id,
        user_id=user["id"],
        email=user["email"],
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        organization_id=organization_id,
        organization_name=org.get("name") if org else None,
        role=_normalize_role(app_session.get("role")),
        platform_role=platform_role,
        is_superadmin=platform_role == "superadmin",
    )


async def require_active_org(request: Request) -> AuthContext:
    ctx = await require_session(request)
    if ctx.organization_id is None and not ctx.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No active organization")
    return ctx


def require_role(*roles: str):
    allowed = {role.lower() for role in roles}

    async def dependency(request: Request) -> AuthContext:
        ctx = await require_active_org(request)
        if ctx.is_superadmin:
            return ctx
        if ctx.role.lower() not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return ctx

    return dependency


def build_return_url(path: str = "/dashboard") -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    normalized = path if path.startswith("/") else f"/{path}"
    return f"{settings.app_base_url.rstrip('/')}{normalized}"


def build_login_redirect(screen_hint: str = "sign-in", return_to: str = "/dashboard") -> str:
    query = urlencode({"screen_hint": screen_hint, "return_to": return_to})
    return f"/auth/login?{query}"
