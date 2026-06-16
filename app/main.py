from __future__ import annotations

import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse

from app.ai import MissingAIConfiguration, parse_event_text
from app.auth import (
    SESSION_COOKIE,
    get_store,
    hash_password,
    hash_token,
    new_token,
    require_user,
    session_expiry,
    verify_password,
)
from app.config import Settings, get_settings
from app.db import EventStore
from app.ics import build_calendar
from app.models import (
    AgendaResponse,
    AuthResponse,
    CalendarListResponse,
    CalendarResponse,
    CreateCalendarRequest,
    LoginRequest,
    ParseRequest,
    ParseResponse,
    RegisterRequest,
    SubscriptionResponse,
    UpdateCalendarRequest,
    UpdateEventRequest,
    UserPublic,
    UserRecord,
)
from app.pages import agenda_page, calendars_page, login_page, maker_page, register_page


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    database = Path(settings.database_path)
    if database.exists() and not database.with_suffix(database.suffix + ".pre-users.bak").exists():
        shutil.copy2(database, database.with_suffix(database.suffix + ".pre-users.bak"))
    EventStore(settings.database_path).init()
    yield


app = FastAPI(title="Calendar Maker", lifespan=lifespan)


def set_session_cookie(
    response: Response,
    token: str,
    settings: Settings,
) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.session_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


def subscription_urls(settings: Settings, path: str) -> SubscriptionResponse:
    https_url = f"{settings.canonical_origin.rstrip('/')}{path}"
    webcal_url = https_url.split("://", 1)[-1]
    return SubscriptionResponse(
        https_url=https_url,
        webcal_url=f"webcal://{webcal_url}",
    )


@app.get("/login", response_class=HTMLResponse)
def login_view() -> str:
    return login_page()


@app.get("/register", response_class=HTMLResponse)
def register_view() -> str:
    return register_page()


@app.get("/", response_class=HTMLResponse)
def maker_view() -> str:
    return maker_page()


@app.get("/agenda", response_class=HTMLResponse)
def agenda_view() -> str:
    return agenda_page()


@app.get("/calendars", response_class=HTMLResponse)
def calendars_view() -> str:
    return calendars_page()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=AuthResponse)
def register(
    request: RegisterRequest,
    response: Response,
    settings: Settings = Depends(get_settings),
    store: EventStore = Depends(get_store),
) -> AuthResponse:
    try:
        user = store.register_user(
            str(request.email),
            hash_password(request.password),
            request.invite_code,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    token = new_token()
    store.create_session(user.id, hash_token(token), session_expiry(settings))
    set_session_cookie(response, token, settings)
    return AuthResponse(user=UserPublic(id=user.id, email=user.email))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(
    request: LoginRequest,
    response: Response,
    settings: Settings = Depends(get_settings),
    store: EventStore = Depends(get_store),
) -> AuthResponse:
    credentials = store.get_user_credentials(str(request.email))
    if credentials is None or not verify_password(credentials["password_hash"], request.password):
        raise HTTPException(status_code=401, detail="invalid email or password")
    user = store.get_user(credentials["id"])
    token = new_token()
    store.create_session(user.id, hash_token(token), session_expiry(settings))
    set_session_cookie(response, token, settings)
    return AuthResponse(user=UserPublic(id=user.id, email=user.email))


@app.post("/api/auth/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    store: EventStore = Depends(get_store),
) -> Response:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        store.delete_session(hash_token(token))
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.status_code = 204
    return response


@app.get("/api/auth/me", response_model=AuthResponse)
def me(user: UserRecord = Depends(require_user)) -> AuthResponse:
    return AuthResponse(user=UserPublic(id=user.id, email=user.email))


@app.get("/api/config/status")
def config_status(
    _: UserRecord = Depends(require_user),
    settings: Settings = Depends(get_settings),
) -> dict[str, str | bool | None]:
    provider_name = None
    model = None
    if settings.effective_qwen_api_key:
        provider_name = "qwen"
        model = settings.qwen_model
    elif settings.effective_openai_api_key:
        provider_name = "openai"
        model = settings.openai_model
    return {
        "ai_provider": provider_name,
        "api_key_configured": provider_name is not None,
        "model": model,
    }


@app.post("/api/parse", response_model=ParseResponse)
def parse_event(
    request: ParseRequest,
    user: UserRecord = Depends(require_user),
    settings: Settings = Depends(get_settings),
    store: EventStore = Depends(get_store),
) -> ParseResponse:
    calendars = store.list_calendars(user.id)
    if not calendars:
        raise HTTPException(status_code=409, detail="create a calendar first")
    try:
        parsed = parse_event_text(request.text, settings, calendars)
    except MissingAIConfiguration as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse event: {exc}") from exc

    calendar_ids = {calendar.id for calendar in calendars}
    selected_id = request.preferred_calendar_id if request.preferred_calendar_id in calendar_ids else None
    selected_id = selected_id or parsed.recommended_calendar_id or calendars[0].id
    event = store.create_pending(user.id, request.text, parsed, selected_id)
    return ParseResponse(
        event=event,
        recommended_calendar_id=parsed.recommended_calendar_id,
        recommendation_reason=parsed.recommendation_reason,
        recommendation_confidence=parsed.recommendation_confidence,
        proposed_calendar=parsed.proposed_calendar,
    )


@app.get("/api/calendars", response_model=CalendarListResponse)
def list_calendars(
    user: UserRecord = Depends(require_user),
    store: EventStore = Depends(get_store),
) -> CalendarListResponse:
    return CalendarListResponse(calendars=store.list_calendars(user.id))


@app.get("/api/calendars/manage", response_model=CalendarListResponse)
def manage_calendars(
    user: UserRecord = Depends(require_user),
    store: EventStore = Depends(get_store),
) -> CalendarListResponse:
    return CalendarListResponse(calendars=store.list_calendars(user.id, include_tokens=True))


@app.post("/api/calendars", response_model=CalendarResponse)
def create_calendar(
    request: CreateCalendarRequest,
    user: UserRecord = Depends(require_user),
    store: EventStore = Depends(get_store),
) -> CalendarResponse:
    return CalendarResponse(
        calendar=store.create_calendar(
            user.id,
            request.name,
            request.color,
            request.description,
        )
    )


@app.patch("/api/calendars/{calendar_id}", response_model=CalendarResponse)
def update_calendar(
    calendar_id: int,
    request: UpdateCalendarRequest,
    user: UserRecord = Depends(require_user),
    store: EventStore = Depends(get_store),
) -> CalendarResponse:
    calendar = store.update_calendar(
        user.id,
        calendar_id,
        request.name,
        request.color,
        request.description,
    )
    if calendar is None:
        raise HTTPException(status_code=404, detail="calendar not found")
    return CalendarResponse(calendar=calendar)


@app.post("/api/calendars/{calendar_id}/regenerate-token", response_model=CalendarResponse)
def regenerate_calendar_token(
    calendar_id: int,
    user: UserRecord = Depends(require_user),
    store: EventStore = Depends(get_store),
) -> CalendarResponse:
    calendar = store.regenerate_calendar_token(user.id, calendar_id)
    if calendar is None:
        raise HTTPException(status_code=404, detail="calendar not found")
    return CalendarResponse(calendar=calendar)


@app.get("/api/calendars/{calendar_id}/subscription", response_model=SubscriptionResponse)
def calendar_subscription(
    calendar_id: int,
    user: UserRecord = Depends(require_user),
    settings: Settings = Depends(get_settings),
    store: EventStore = Depends(get_store),
) -> SubscriptionResponse:
    calendar = store.get_calendar(user.id, calendar_id, include_token=True)
    if calendar is None:
        raise HTTPException(status_code=404, detail="calendar not found")
    return subscription_urls(settings, f"/calendars/{calendar.id}.ics?token={calendar.token}")


@app.get("/api/feeds/all/subscription", response_model=SubscriptionResponse)
def all_subscription(
    user: UserRecord = Depends(require_user),
    settings: Settings = Depends(get_settings),
) -> SubscriptionResponse:
    return subscription_urls(settings, f"/feeds/all.ics?token={user.all_feed_token}")


@app.post("/api/feeds/all/regenerate-token", response_model=SubscriptionResponse)
def regenerate_all_feed(
    user: UserRecord = Depends(require_user),
    settings: Settings = Depends(get_settings),
    store: EventStore = Depends(get_store),
) -> SubscriptionResponse:
    updated = store.regenerate_all_feed_token(user.id)
    return subscription_urls(settings, f"/feeds/all.ics?token={updated.all_feed_token}")


@app.post("/api/events/{event_id}/confirm", response_model=ParseResponse)
def confirm_event(
    event_id: int,
    request: UpdateEventRequest,
    user: UserRecord = Depends(require_user),
    store: EventStore = Depends(get_store),
) -> ParseResponse:
    try:
        event = store.update_event(
            user.id,
            event_id,
            request,
            request.calendar_id,
            confirm=True,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")
    return ParseResponse(
        event=event,
        recommended_calendar_id=None,
        recommendation_reason="",
        recommendation_confidence=0,
        proposed_calendar=None,
    )


@app.patch("/api/events/{event_id}", response_model=ParseResponse)
def edit_event(
    event_id: int,
    request: UpdateEventRequest,
    user: UserRecord = Depends(require_user),
    store: EventStore = Depends(get_store),
) -> ParseResponse:
    try:
        event = store.update_event(user.id, event_id, request, request.calendar_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")
    return ParseResponse(
        event=event,
        recommended_calendar_id=None,
        recommendation_reason="",
        recommendation_confidence=0,
        proposed_calendar=None,
    )


@app.delete("/api/events/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    user: UserRecord = Depends(require_user),
    store: EventStore = Depends(get_store),
) -> Response:
    if not store.delete_event(user.id, event_id):
        raise HTTPException(status_code=404, detail="event not found")
    return Response(status_code=204)


@app.get("/api/agenda", response_model=AgendaResponse)
def agenda(
    include_past: bool = Query(default=False),
    calendar_id: int | None = Query(default=None),
    user: UserRecord = Depends(require_user),
    store: EventStore = Depends(get_store),
) -> AgendaResponse:
    now = datetime.now(timezone.utc)
    start = None if include_past else now
    end = now + timedelta(days=90)
    return AgendaResponse(
        events=store.agenda_events(user.id, start=start, end=end, calendar_id=calendar_id)
    )


@app.get("/calendars/{calendar_id}.ics")
def calendar_feed(
    calendar_id: int,
    token: str = Query(default=""),
    store: EventStore = Depends(get_store),
) -> Response:
    calendar = store.find_calendar_by_token(calendar_id, token)
    if calendar is None:
        raise HTTPException(status_code=401, detail="invalid calendar token")
    content = build_calendar(
        store.confirmed_events(calendar.user_id, calendar_id=calendar_id),
        calendar.name,
    )
    return Response(
        content=content,
        media_type="text/calendar; charset=utf-8",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/feeds/all.ics")
def all_calendar_feed(
    token: str = Query(default=""),
    store: EventStore = Depends(get_store),
) -> Response:
    user = store.user_by_feed_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid feed token")
    content = build_calendar(store.confirmed_events(user.id), "All Calendars")
    return Response(
        content=content,
        media_type="text/calendar; charset=utf-8",
        headers={"Cache-Control": "no-store"},
    )
