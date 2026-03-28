"""
Authentication routes backed by WorkOS AuthKit and Redis app sessions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.auth import (
    build_return_url,
    clear_session_cookie,
    consume_auth_state,
    create_app_session,
    create_auth_state,
    delete_app_session,
    get_app_session,
    get_org,
    get_user,
    get_workos_client,
    list_memberships_for_user,
    list_orgs,
    require_session,
    set_active_organization,
    set_session_cookie,
    upsert_identity,
)
from app.config import settings
from app.models import MeResponse, OrganizationSummary, OrganizationSwitchRequest

router = APIRouter()


async def _build_me_response(context) -> MeResponse:
    organization = await get_org(context.organization_id) if context.organization_id else None
    memberships = await list_memberships_for_user(context.user_id)
    organizations: list[OrganizationSummary] = []
    for membership in memberships:
        org = await get_org(membership["organization_id"])
        if org:
            organizations.append(
                OrganizationSummary(
                    id=org["id"],
                    name=org["name"],
                    slug=org["slug"],
                    role=membership["role"],
                )
            )

    return MeResponse(
        user_id=context.user_id,
        email=context.email,
        first_name=context.first_name,
        last_name=context.last_name,
        role=context.role,
        platform_role=context.platform_role,
        is_superadmin=context.is_superadmin,
        organization=OrganizationSummary(
            id=organization["id"],
            name=organization["name"],
            slug=organization["slug"],
            role=context.role,
        )
        if organization
        else None,
        organizations=organizations,
    )


@router.get("/auth/login")
async def login(
    screen_hint: str = Query("sign-in"),
    return_to: str = Query("/dashboard"),
):
    if not settings.workos_cookie_password:
        raise HTTPException(status_code=503, detail="WorkOS session password is not configured")

    state = await create_auth_state(screen_hint=screen_hint, return_to=return_to)
    authorization_url = get_workos_client().user_management.get_authorization_url(
        redirect_uri=settings.workos_redirect_uri,
        state=state,
        provider="authkit",
        screen_hint="sign-up" if screen_hint == "sign-up" else "sign-in",
    )
    return RedirectResponse(authorization_url, status_code=302)


@router.get("/auth/callback")
async def callback(request: Request, code: str, state: str):
    state_data = await consume_auth_state(state)
    auth_response = get_workos_client().user_management.authenticate_with_code(
        code=code,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        session={
            "seal_session": True,
            "cookie_password": settings.workos_cookie_password,
        },
    )
    if not auth_response.sealed_session:
        raise HTTPException(status_code=502, detail="WorkOS did not return a sealed session")

    identity = await upsert_identity(auth_response)
    workos_session = get_workos_client().user_management.load_sealed_session(
        sealed_session=auth_response.sealed_session,
        cookie_password=settings.workos_cookie_password,
    )
    session_auth = workos_session.authenticate()
    if not session_auth.authenticated:
        raise HTTPException(status_code=502, detail="WorkOS session authentication failed")
    app_session_id = await create_app_session(
        sealed_session=auth_response.sealed_session,
        workos_session_id=session_auth.session_id,
        user_id=identity["user"]["id"],
        organization_id=identity["organization"]["id"],
        role=identity["membership"]["role"],
        platform_role=identity["platform_role"],
    )
    response = RedirectResponse(build_return_url(state_data["return_to"]), status_code=302)
    set_session_cookie(response, app_session_id)
    return response


@router.post("/auth/logout")
async def logout(request: Request):
    response = JSONResponse({"ok": True})
    session_id = request.cookies.get(settings.auth_session_cookie_name)
    if session_id:
        app_session = await get_app_session(session_id)
        if app_session and app_session.get("workos_session_id"):
            try:
                get_workos_client().user_management.revoke_session(
                    session_id=app_session["workos_session_id"]
                )
            except Exception:
                pass
        await delete_app_session(session_id)
    clear_session_cookie(response)
    return response


@router.get("/api/me", response_model=MeResponse)
async def me(context=Depends(require_session)):
    return await _build_me_response(context)


@router.get("/api/me/organizations", response_model=list[OrganizationSummary])
async def my_organizations(context=Depends(require_session)):
    if context.is_superadmin:
        orgs = await list_orgs()
        return [
            OrganizationSummary(id="all", name="All organizations", slug="all", role="superadmin"),
            *[
                OrganizationSummary(
                    id=org["id"],
                    name=org["name"],
                    slug=org["slug"],
                    role="superadmin",
                )
                for org in orgs
            ],
        ]

    memberships = await list_memberships_for_user(context.user_id)
    results: list[OrganizationSummary] = []
    for membership in memberships:
        org = await get_org(membership["organization_id"])
        if org:
            results.append(
                OrganizationSummary(
                    id=org["id"],
                    name=org["name"],
                    slug=org["slug"],
                    role=membership["role"],
                )
            )
    return results


@router.post("/api/me/organizations/switch", response_model=MeResponse)
async def switch_organization(
    body: OrganizationSwitchRequest,
    request: Request,
    context=Depends(require_session),
):
    target = None if body.organization_id in ("", "all") else body.organization_id

    if context.is_superadmin:
        if target is not None and not await get_org(target):
            raise HTTPException(status_code=404, detail="Organization not found")
        await set_active_organization(context.session_id, target)
    else:
        user = await get_user(context.user_id)
        if target != user.get("organization_id"):
            raise HTTPException(status_code=403, detail="Forbidden")
        await set_active_organization(context.session_id, target)

    refreshed = await require_session(request)
    return await _build_me_response(refreshed)
