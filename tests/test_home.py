import re

import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


@pytest.mark.smoke
def test_home_page_title_and_meta(home: HomePage, page: Page):
    expect(page).to_have_title(re.compile(r"ICS .*creditcarduitgever"))
    expect(page.locator("link[rel='canonical']")).to_have_attribute("href", "https://www.icscards.nl/")
    expect(page.locator("meta[name='description']")).to_have_attribute("content", re.compile("creditcard"))
    expect(page.locator("html")).to_have_attribute("lang", "nl")


@pytest.mark.smoke
def test_home_page_has_visible_heading(home: HomePage):
    expect(home.main_heading).to_be_visible()


@pytest.mark.smoke
def test_header_shows_private_and_business_links(home: HomePage):
    expect(home.private_link).to_have_attribute("aria-current", "page")
    expect(home.business_link).to_have_attribute("href", "/zakelijk")


def test_navigate_to_business(home: HomePage, page: Page):
    home.go_to_business()
    expect(page).to_have_url(re.compile(r"/zakelijk/?$"))


def test_menu_button_opens_menu_dialog(home: HomePage, page: Page):
    page.set_viewport_size({"width": 390, "height": 844})
    home.open_menu_button.click()
    expect(page.get_by_role("dialog").first).to_be_visible()


@pytest.mark.responsive
@pytest.mark.parametrize("size", [{"width": 390, "height": 844}, {"width": 1440, "height": 900}])
def test_home_renders_at_viewport(home: HomePage, page: Page, size):
    page.set_viewport_size(size)
    expect(home.main_heading).to_be_visible()


def test_no_broken_internal_links(home: HomePage, page: Page):
    hrefs = page.eval_on_selector_all(
        "a[href^='/']:not([href^='//'])", "els => [...new Set(els.map(e => e.getAttribute('href')))]"
    )
    assert hrefs, "expected internal links on the home page"
    failures = []
    for href in hrefs[:25]:
        response = page.request.get(href.split("#")[0] or "/")
        if response.status >= 400:
            failures.append((href, response.status))
    assert not failures, f"Broken links: {failures}"
