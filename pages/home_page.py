import re

from playwright.sync_api import Locator

from pages.base_page import BasePage


class HomePage(BasePage):
    path = "/"

    @property
    def header(self) -> Locator:
        return self.page.locator("header")

    @property
    def private_link(self) -> Locator:
        return self.header.get_by_role("link", name="Privé", exact=True)

    @property
    def business_link(self) -> Locator:
        return self.header.get_by_role("link", name="Zakelijk", exact=True)

    @property
    def open_menu_button(self) -> Locator:
        return self.page.get_by_role("button", name=re.compile(r"^Open menu ?dialo(g|oog)$")).first

    @property
    def main_heading(self) -> Locator:
        return self.page.get_by_role("heading", level=1).first

    def go_to_business(self) -> None:
        self.business_link.click()
