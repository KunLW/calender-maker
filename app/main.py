from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse, Response

from app.ai import MissingAIConfiguration, parse_event_text
from app.config import Settings, get_settings
from app.db import EventStore
from app.ics import build_calendar
from app.models import ParseRequest, ParseResponse, UpdateEventRequest


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


@app.get("/api/config/status")
def config_status(settings: Settings = Depends(get_settings)) -> dict[str, str | bool | None]:
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
    request: UpdateEventRequest,
    _: None = Depends(require_app_token),
    store: EventStore = Depends(get_store),
) -> ParseResponse:
    existing = store.get(event_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="event not found")
    if existing.status != "pending":
        raise HTTPException(status_code=409, detail="event already confirmed")

    event = store.update_and_confirm(event_id, request)
    if event is None:
        raise HTTPException(status_code=409, detail="event could not be confirmed")
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
    textarea,
    input {
      box-sizing: border-box;
      width: 100%;
      resize: vertical;
      border: 1px solid #bcc5b4;
      border-radius: 6px;
      padding: 12px;
      font-size: 16px;
      line-height: 1.5;
    }
    textarea {
      min-height: 130px;
    }
    input {
      min-height: 44px;
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
    input:disabled,
    textarea:disabled {
      background: #f1f3ee;
      color: #677066;
      cursor: not-allowed;
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
    .form-grid {
      display: grid;
      gap: 12px;
    }
    label {
      display: grid;
      gap: 6px;
      color: #677066;
      font-size: 14px;
    }
    label span {
      color: #20231f;
      font-size: 16px;
    }
    .error {
      color: #a4362a;
    }
    .ok {
      color: #1f6f61;
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Calendar Maker</h1>
      <div class="muted">输入一句话，确认后写入订阅日历。</div>
      <div id="configStatus" class="muted">检查 AI 配置中...</div>
    </header>
    <section class="panel">
      <textarea id="text" placeholder="例如：明天下午三点和王总开会，在腾讯会议，预计一小时"></textarea>
      <div class="actions">
        <button id="parseBtn">解析</button>
        <span id="status" class="muted"></span>
      </div>
    </section>
    <section id="eventPanel" class="panel event">
      <div class="form-grid">
        <label>标题<input id="title" type="text"></label>
        <label>开始<input id="start" type="datetime-local"></label>
        <label>结束<input id="end" type="datetime-local"></label>
        <label>地点<input id="location" type="text"></label>
        <label>备注<textarea id="description"></textarea></label>
      </div>
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
    const configStatusEl = document.getElementById("configStatus");
    const panel = document.getElementById("eventPanel");
    const appToken = new URLSearchParams(window.location.search).get("token") || "";
    let currentEventId = null;
    let currentTimezone = "Asia/Shanghai";
    const editableFields = ["title", "start", "end", "location", "description"].map((id) => {
      return document.getElementById(id);
    });

    function toDatetimeLocal(value) {
      const date = new Date(value);
      const offsetMs = date.getTimezoneOffset() * 60000;
      return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
    }

    function fromDatetimeLocal(value) {
      return new Date(value).toISOString();
    }

    function setEvent(event) {
      currentEventId = event.id;
      currentTimezone = event.timezone || currentTimezone;
      setEditorLocked(false);
      document.getElementById("title").value = event.title;
      document.getElementById("start").value = toDatetimeLocal(event.start);
      document.getElementById("end").value = toDatetimeLocal(event.end);
      document.getElementById("location").value = event.location || "";
      document.getElementById("description").value = event.description || event.source_text;
      panel.classList.add("visible");
    }

    function setEditorLocked(locked) {
      editableFields.forEach((field) => {
        field.disabled = locked;
      });
      confirmBtn.disabled = locked;
    }

    function readEventForm() {
      return {
        title: document.getElementById("title").value.trim(),
        start: fromDatetimeLocal(document.getElementById("start").value),
        end: fromDatetimeLocal(document.getElementById("end").value),
        timezone: currentTimezone,
        location: document.getElementById("location").value.trim() || null,
        description: document.getElementById("description").value.trim() || null
      };
    }

    async function loadConfigStatus() {
      try {
        const response = await fetch("/api/config/status");
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "配置检查失败");
        if (data.api_key_configured) {
          configStatusEl.textContent = `AI 已配置：${data.ai_provider} / ${data.model}`;
          configStatusEl.className = "muted ok";
        } else {
          configStatusEl.textContent = "AI 未配置：请在启动服务前设置 QWEN_API_KEY，或写入 .env";
          configStatusEl.className = "muted error";
        }
      } catch (error) {
        configStatusEl.textContent = error.message;
        configStatusEl.className = "muted error";
      }
    }

    loadConfigStatus();

    parseBtn.addEventListener("click", async () => {
      const text = document.getElementById("text").value.trim();
      if (!text) return;
      parseBtn.disabled = true;
      setEditorLocked(false);
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
          headers: {"Content-Type": "application/json", "X-App-Token": appToken},
          body: JSON.stringify(readEventForm())
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "保存失败");
        confirmStatusEl.textContent = "已添加到订阅日历";
        setEditorLocked(true);
        document.getElementById("text").value = "";
        statusEl.textContent = "可以继续输入下一条";
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
