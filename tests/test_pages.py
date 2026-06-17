from app.pages import calendars_page


def test_calendar_subscription_ui_uses_webcal_for_subscribe_and_https_for_download() -> None:
    page = calendars_page()

    assert 'href="${urls.webcal_url}">Subscribe to Apple Calendar' in page
    assert 'href="${urls.https_url}">Download ICS' in page
    assert 'data-url="${esc(urls.https_url)}">Copy' in page
