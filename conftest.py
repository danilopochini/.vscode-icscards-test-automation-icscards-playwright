import base64
import webbrowser
from pathlib import Path

import pytest
from playwright.sync_api import Page

from pages.home_page import HomePage
from report_builder import Report

_report = Report()


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
    # Record the call phase, plus setup failures/skips (the call phase never runs then)
    if report.when == "call" or (report.when == "setup" and not report.passed):
        shot = ""
        page = item.funcargs.get("page")
        if page is not None and not page.is_closed():
            try:
                shot = base64.b64encode(page.screenshot()).decode()
            except Exception:
                pass
        doc = [line.strip() for line in (item.obj.__doc__ or "").strip().splitlines() if line.strip()]
        title = doc[0] if doc else item.originalname.removeprefix("test_").replace("_", " ").capitalize()
        callspec = getattr(item, "callspec", None)
        variant = callspec.id.split("-", 1)[1] if callspec and "-" in callspec.id else ""
        if variant:
            title = f"{title} ({variant})"
        browser = item.config.getoption("browser") or ["chromium"]
        _report.add_test(
            name=title,
            steps=doc[1:],
            tags=[m.name for m in item.iter_markers() if m.name in ("smoke", "responsive")] + [browser[0]],
            status=report.outcome,
            duration=report.duration,
            error=report.longreprtext if report.failed else "",
            screenshot_b64=shot,
        )


def pytest_addoption(parser):
    parser.addoption("--no-open-report", action="store_true", help="do not open report.html when the run ends")


def pytest_sessionfinish(session, exitstatus):
    _report.base_url = session.config.getoption("base_url") or ""
    report_path = Path("report.html").resolve()
    _report.write(report_path)
    if not session.config.getoption("--no-open-report"):
        webbrowser.open(report_path.as_uri())
