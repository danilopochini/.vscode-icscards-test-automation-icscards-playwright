import re

import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


@pytest.mark.smoke
def test_home_page_title_and_meta(home: HomePage, page: Page):
    """Page title and metadata are correct
    Given I open the home page
    Then the page title matches "ICS .*creditcarduitgever"
    And the canonical link is "https://www.icscards.nl/"
    And the meta description contains "creditcard"
    And the html language is "nl"
    """
    expect(page).to_have_title(re.compile(r"ICS .*creditcarduitgever"))
    expect(page.locator("link[rel='canonical']")).to_have_attribute("href", "https://www.icscards.nl/")
    expect(page.locator("meta[name='description']")).to_have_attribute("content", re.compile("creditcard"))
    expect(page.locator("html")).to_have_attribute("lang", "nl")


@pytest.mark.smoke
def test_home_page_has_visible_heading(home: HomePage):
    """Home page shows a main heading
    Given I open the home page
    Then the main heading is visible
    """
    expect(home.main_heading).to_be_visible()


@pytest.mark.smoke
def test_header_shows_private_and_business_links(home: HomePage):
    """Header shows private and business links
    Given I open the home page
    Then the "Privé" header link is the current page
    And the "Zakelijk" header link points to "/zakelijk"
    """
    expect(home.private_link).to_have_attribute("aria-current", "page")
    expect(home.business_link).to_have_attribute("href", "/zakelijk")


def test_navigate_to_business(home: HomePage, page: Page):
    """Navigate to business
    Given I open the home page
    When I click the "Zakelijk" header link
    Then the url ends with /zakelijk
    """
    home.go_to_business()
    expect(page).to_have_url(re.compile(r"/zakelijk/?$"))


def test_menu_button_opens_menu_dialog(home: HomePage, page: Page):
    """Menu button opens the menu dialog on mobile
    Given I open the home page
    And the viewport is 390 by 844
    When I click the open menu button
    Then a dialog is visible
    """
    page.set_viewport_size({"width": 390, "height": 844})
    home.open_menu_button.click()
    expect(page.get_by_role("dialog").first).to_be_visible()


@pytest.mark.responsive
@pytest.mark.parametrize(
    "size",
    [{"width": 390, "height": 844}, {"width": 1440, "height": 900}],
    ids=["mobile 390x844", "desktop 1440x900"],
)
def test_home_renders_at_viewport(home: HomePage, page: Page, size):
    """Home page renders at different viewports
    Given I open the home page
    And the viewport is set to the given size
    Then the main heading is visible
    """
    page.set_viewport_size(size)
    expect(home.main_heading).to_be_visible()


def test_no_broken_internal_links(home: HomePage, page: Page):
    """No broken internal links
    Given I open the home page
    Then the first 25 internal links respond without errors
    """
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
