# Calendar Maker

Turn a natural-language sentence into an editable calendar event, let AI recommend the best calendar, then publish confirmed events through private ICS subscriptions.

## Features

- Invite-only email/password accounts
- Argon2 password hashing and server-side cookie sessions
- Strict per-user ownership for calendars and events
- Qwen/OpenAI-compatible structured event parsing
- AI calendar recommendations and proposed new calendars
- Editable event confirmation with duplicate-submit protection
- Agenda view across all calendars with edit and delete
- Calendar colors and descriptions
- Per-calendar and combined ICS feeds
- Apple Calendar `webcal://` links and copyable HTTPS links
- Revocable subscription tokens

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.admin create-invite
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/register` and register with the generated single-use invite code.

## Configuration

Important settings:

```env
QWEN_API_KEY=
QWEN_MODEL=qwen-plus
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
APP_TIMEZONE=Asia/Shanghai
DATABASE_PATH=data/calendar.db
CANONICAL_ORIGIN=https://quantumman.tech
SESSION_COOKIE_SECURE=false
SESSION_DAYS=30
```

Set `SESSION_COOKIE_SECURE=true` in production after HTTPS is operational. Environment variables take precedence over `.env`.

## Accounts and Invites

Generate an invite from the deployment directory:

```bash
.venv/bin/python -m app.admin create-invite
```

Each code can register one account. The first registered account atomically claims calendars and events created by the previous single-user version. Later accounts receive a new default calendar.

Sessions are stored server-side. The browser only receives an opaque `HttpOnly` session cookie.

## Pages

- `/` — AI event creation and confirmation
- `/agenda` — combined agenda with calendar filters, editing, and deletion
- `/calendars` — calendar metadata and subscription management
- `/login` and `/register` — account access

## Subscriptions

Each calendar exposes:

```text
https://quantumman.tech/calendars/{calendar_id}.ics?token=...
webcal://quantumman.tech/calendars/{calendar_id}.ics?token=...
```

Each user also has a combined feed:

```text
https://quantumman.tech/feeds/all.ics?token=...
webcal://quantumman.tech/feeds/all.ics?token=...
```

Tokens are visible only from the authenticated calendar-management page and can be regenerated to invalidate old links.

## Database Migration

Startup applies additive SQLite migrations for users, sessions, invite codes, ownership, calendar colors, and descriptions. Before the first user migration, the application creates:

```text
data/calendar.db.pre-users.bak
```

Keep this backup until the first account has registered and legacy ownership has been verified.

## Tests

```bash
pytest
```

Coverage includes invite consumption, Argon2 hashing, session lookup, user isolation, AI recommendation validation, event confirmation, agenda operations, ICS isolation, webcal/HTTPS URLs, and token regeneration.

## ECS Deployment

Update using Git rather than copying files:

```bash
cd /opt/calendar_maker
git pull --ff-only origin main
source .venv/bin/activate
pip install -r requirements.txt
pytest
systemctl restart calendar-maker
```

Production `.env` additions:

```env
CANONICAL_ORIGIN=https://quantumman.tech
SESSION_COOKIE_SECURE=true
```

Then generate the first invite:

```bash
cd /opt/calendar_maker
.venv/bin/python -m app.admin create-invite
```

The existing Nginx Proxy Manager should forward the domain to the application. HTTPS must be functioning before Apple Calendar subscription links are used.
