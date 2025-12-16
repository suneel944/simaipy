from playwright.sync_api import Page

from .base_page import BasePage
from .chat_page import ChatPage


class LoginPage(BasePage):
    """Page object modelling the login page."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page)
        self.base_url = base_url
        self._locator_login_button = "xpath=.//button//*[text()='Log in']"
        self._locator_email_input = "#email"
        self._locator_password_input = "#password"
        self._locator_submit_button = {"role": "button", "name": "Log in"}

    def login(self, email, password) -> ChatPage:
        self.goto(self.base_url)
        self.page.locator(self._locator_login_button).click()
        self.page.locator(self._locator_email_input).fill(email)
        self.page.locator(self._locator_password_input).fill(password)
        self.page.locator("form").get_by_role(
            role="button",  # type: ignore[arg-type]
            name=self._locator_submit_button["name"],
        ).click()
        return ChatPage(self.page)
