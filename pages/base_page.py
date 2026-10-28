from playwright.sync_api import Page


class BasePage:
    path = "/"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        self.page.goto(f"{self.base_url}{self.path}", wait_until="domcontentloaded")
        self.dismiss_cookie_banner()

    def dismiss_cookie_banner(self) -> None:
        # CookieFirst renders the consent dialog asynchronously; it may not appear at all.
        reject = self.page.locator("[data-cookiefirst-action='reject']")
        try:
            reject.first.click(timeout=5000)
        except Exception:
            pass
