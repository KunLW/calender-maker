from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse, Response

from app.ai import MissingAIConfiguration, parse_event_text
from app.config import Settings, get_settings
from app.db import EventStore
from app.ics import build_calendar
from app.models import ParseRequest, ParseResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    EventStore(get_settings().database_path).init()
    yield


app = FastAPI(title="Calendar Maker", lifespan=lifespan)


def get_store(settings: Settings = Depends(get_settings)) -> EventStore:
    return EventStore(settings.database_path)


def require_app_token(
    token: str = Query(default=""),
    x_app_token: str = Header(default=""),
    settings: Settings = Depends(get_settings),
) -> None:
    if settings.app_token and token != settings.app_token and x_app_token != settings.app_token:
        raise HTTPException(status_code=401, detail="invalid app token")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_HTML


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/parse", response_model=ParseResponse)
def parse_event(
    request: ParseRequest,
    _: None = Depends(require_app_token),
    settings: Settings = Depends(get_settings),
    store: EventStore = Depends(get_store),
) -> ParseResponse:
    try:
        parsed = parse_event_text(request.text, settings)
    except MissingAIConfiguration as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse event: {exc}") from exc

    event = store.create_pending(request.text, parsed)
    return ParseResponse(event=event)


@app.post("/api/events/{event_id}/confirm", response_model=ParseResponse)
def confirm_event(
    event_id: int,
    _: None = Depends(require_app_token),
    store: EventStore = Depends(get_store),
) -> ParseResponse:
    event = store.confirm(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")
    return ParseResponse(event=event)


@app.get("/calendar.ics")
def calendar_feed(
    token: str = Query(default=""),
    settings: Settings = Depends(get_settings),
    store: EventStore = Depends(get_store),
) -> Response:
    if token != settings.calendar_token:
        raise HTTPException(status_code=401, detail="invalid calendar token")
    content = build_calendar(store.confirmed_events(), settings.calendar_name)
    return Response(
        content=content,
        media_type="text/calendar; charset=utf-8",
        headers={"Cache-Control": "no-store"},
    )


INDEX_HTML = """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Calendar Maker</title>
  <style>
    :root {
      color-scheme: light;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f7f4;
      color: #20231f;
    }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
    }
    main {
      width: min(760px, calc(100vw - 32px));
      display: grid;
      gap: 16px;
    }
    h1 {
      margin: 0;
      font-size: 28px;
      font-weight: 700;
    }
    .panel {
      background: #ffffff;
      border: 1px solid #d9ddd2;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 10px 30px rgba(32, 35, 31, 0.08);
    }
    textarea {
      box-sizing: border-box;
      width: 100%;
      min-height: 130px;
      resize: vertical;
      border: 1px solid #bcc5b4;
      border-radius: 6px;
      padding: 12px;
      font-size: 16px;
      line-height: 1.5;
    }
    button {
      border: 0;
      border-radius: 6px;
      background: #1f6f61;
      color: white;
      padding: 10px 14px;
      font-size: 15px;
      cursor: pointer;
    }
    button:disabled {
      cursor: not-allowed;
      opacity: 0.6;
    }
    .actions {
      display: flex;
      gap: 10px;
      align-items: center;
      margin-top: 12px;
    }
    .muted {
      color: #677066;
      font-size: 14px;
    }
    .event {
      display: none;
      gap: 8px;
    }
    .event.visible {
      display: grid;
    }
    dl {
      display: grid;
      grid-template-columns: 80px 1fr;
      gap: 8px 12px;
      margin: 0;
    }
    dt {
      color: #677066;
    }
    dd {
      margin: 0;
    }
    .error {
      color: #a4362a;
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Calendar Maker</h1>
      <div class="muted">输入一句话，确认后写入订阅日历。</div>
    </header>
    <section class="panel">
      <textarea id="text" placeholder="例如：明天下午三点和王总开会，在腾讯会议，预计一小时"></textarea>
      <div class="actions">
        <button id="parseBtn">解析</button>
        <span id="status" class="muted"></span>
      </div>
    </section>
    <section id="eventPanel" class="panel event">
      <dl>
        <dt>标题</dt><dd id="title"></dd>
        <dt>开始</dt><dd id="start"></dd>
        <dt>结束</dt><dd id="end"></dd>
        <dt>地点</dt><dd id="location"></dd>
        <dt>备注</dt><dd id="description"></dd>
      </dl>
      <div class="actions">
        <button id="confirmBtn">确认添加</button>
        <span id="confirmStatus" class="muted"></span>
      </div>
    </section>
  </main>
  <script>
    const parseBtn = document.getElementById("parseBtn");
    const confirmBtn = document.getElementById("confirmBtn");
    const statusEl = document.getElementById("status");
    const confirmStatusEl = document.getElementById("confirmStatus");
    const panel = document.getElementById("eventPanel");
    const appToken = new URLSearchParams(window.location.search).get("token") || "";
    let currentEventId = null;

    function setEvent(event) {
      currentEventId = event.id;
      document.getElementById("title").textContent = event.title;
      document.getElementById("start").textContent = new Date(event.start).toLocaleString();
      document.getElementById("end").textContent = new Date(event.end).toLocaleString();
      document.getElementById("location").textContent = event.location || "";
      document.getElementById("description").textContent = event.description || event.source_text;
      panel.classList.add("visible");
    }

    parseBtn.addEventListener("click", async () => {
      const text = document.getElementById("text").value.trim();
      if (!text) return;
      parseBtn.disabled = true;
      statusEl.textContent = "解析中...";
      statusEl.className = "muted";
      confirmStatusEl.textContent = "";
      try {
        const response = await fetch("/api/parse", {
          method: "POST",
          headers: {"Content-Type": "application/json", "X-App-Token": appToken},
          body: JSON.stringify({text})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "解析失败");
        setEvent(data.event);
        statusEl.textContent = "请确认解析结果";
      } catch (error) {
        statusEl.textContent = error.message;
        statusEl.className = "muted error";
      } finally {
        parseBtn.disabled = false;
      }
    });

    confirmBtn.addEventListener("click", async () => {
      if (!currentEventId) return;
      confirmBtn.disabled = true;
      confirmStatusEl.textContent = "保存中...";
      try {
        const response = await fetch(`/api/events/${currentEventId}/confirm`, {
          method: "POST",
          headers: {"X-App-Token": appToken}
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "保存失败");
        confirmStatusEl.textContent = "已添加到订阅日历";
      } catch (error) {
        confirmStatusEl.textContent = error.message;
        confirmStatusEl.className = "muted error";
      } finally {
        confirmBtn.disabled = false;
      }
    });
  </script>
</body>
</html>
"""
