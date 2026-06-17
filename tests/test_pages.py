from fastapi.testclient import TestClient

import app.main as main
from app.pages import calendar_detail_page, calendars_page, maker_page


def test_calendar_subscription_ui_uses_webcal_for_subscribe_and_https_for_download() -> None:
    page = calendars_page()

    assert 'href="${urls.webcal_url}"' in page
    assert "function downloadUrl(urls)" in page
    assert 'href="${downloadUrl(urls)}"' in page
    assert 'class="calendar-card"' in page
    assert 'class="calendar-create-card"' in page
    assert "calendars.createTitle" in page
    assert "calendars.settings" in page
    assert "/edit" in page
    assert 'data-url="${esc(urls.https_url)}"' not in page
    assert "calendars.feedUrl" not in page


def test_calendar_detail_page_supports_editing_and_regeneration() -> None:
    page = calendar_detail_page(7)

    assert "const calendarId=7" in page
    assert 'data-i18n="calendars.regenerate"' in page
    assert 'method:"PATCH"' in page
    assert "/regenerate-token" in page


def test_pages_include_language_switcher_and_pwa_icons() -> None:
    page = maker_page()

    assert 'class="language-select"' in page
    assert "localStorage.setItem(LANGUAGE_KEY,value)" in page
    assert '<link rel="manifest" href="/manifest.webmanifest">' in page
    assert '<link rel="icon" href="/static/icons/app-icon.svg" type="image/svg+xml">' in page
    assert '<link rel="apple-touch-icon" href="/static/icons/app-icon.svg">' in page


def test_manifest_exposes_app_icon_metadata() -> None:
    with TestClient(main.app) as client:
        response = client.get("/manifest.webmanifest")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/manifest+json")
    manifest = response.json()
    assert manifest["name"] == "Calendar Maker"
    assert manifest["short_name"] == "Calendar"
    assert manifest["display"] == "standalone"
    assert manifest["theme_color"] == "#f6f7f3"
    assert manifest["icons"][0]["src"] == "/static/icons/app-icon.svg"
    assert manifest["icons"][0]["sizes"] == "any"
