from __future__ import annotations

from playwright.sync_api import Page, expect


class BasePage:
    """Base page object with common Playwright helpers."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, url: str) -> None:
        self.page.goto(url, wait_until="networkidle")

    def expect_visible(self, selector: str) -> None:
        expect(self.page.locator(selector)).to_be_visible()


__all__ = ["BasePage"]
