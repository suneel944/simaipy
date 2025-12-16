from __future__ import annotations

from playwright.sync_api import Page

from .base_page import BasePage


class ChatPage(BasePage):
    """Page object modelling the chatbot UI."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self._locator_input_box = "#chat-input"

    def send_message(self, text: str) -> str:
        """Send a message and return the last bot reply text."""
        self.page.locator(self._locator_input_box).type(text)
        with self.page.expect_response(
            lambda res: res.url.endswith("/api/chat/completed")
        ) as response_info:
            self.page.locator(self._locator_input_box).press("Enter")
        response = response_info.value
        payload = response.json()
        messages = payload.get("messages")

        if not isinstance(messages, list) or not messages:
            raise RuntimeError(f"Unexpected chat payload shape: {payload!r}")

        for message in reversed(messages):
            if message.get("role") == "assistant":
                return message.get("content")
        raise RuntimeError(f"No assistant message found in payload: {payload!r}")


__all__ = ["ChatPage"]
