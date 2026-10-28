import base64

import pytest
from pytest_html import extras
from playwright.sync_api import Page

from pages.home_page import HomePage


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "locale": "nl-NL", "timezone_id": "Europe/Amsterdam"}


@pytest.fixture
def home(page: Page, base_url: str) -> HomePage:
    home_page = HomePage(page, base_url)
    home_page.open()
    return home_page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    page = item.funcargs.get("page")
    if page is None or page.is_closed():
        return
    try:
        image = base64.b64encode(page.screenshot()).decode()
    except Exception:
        return
    report.extras = getattr(report, "extras", []) + [extras.png(image, name="screenshot")]
