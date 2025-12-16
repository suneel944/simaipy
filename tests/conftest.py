from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest
from playwright.sync_api import Page

from simaipy.config_loader import build_settings
from simaipy.report_generator import TestReportGenerator
from tests.pages import ChatPage
from tests.pages.login_page import LoginPage


@pytest.fixture(scope="session")
def settings():
    """Session-scoped configuration object built via CLI/env/YAML precedence."""
    return build_settings()


@pytest.fixture(scope="session")
def test_cases() -> List[Dict[str, Any]]:
    """Load shared chatbot test scenarios from JSON."""
    data_path = Path(__file__).parent / "test_data" / "data.json"
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def chat_page(page: Page, settings) -> ChatPage:
    """Fully composed page object for interacting with the chatbot."""
    if not settings.user_email or not settings.user_password:
        pytest.skip(
            "UI tests require credentials. Set SIMAI_USER_EMAIL and SIMAI_USER_PASSWORD "
            "(or provide user_email/user_password via YAML/CLI)."
        )
    login_page = LoginPage(page, settings.base_url)
    return login_page.login(settings.user_email, settings.user_password)


@pytest.fixture(scope="session")
def browser_type_launch_args(
    browser_type_launch_args: Dict[str, Any],
) -> Dict[str, Any]:
    """Launch browser in maximised window (not just a larger viewport)."""
    args = list(browser_type_launch_args.get("args", []))
    if "--start-maximized" not in args:
        args.append("--start-maximized")
    return {
        **browser_type_launch_args,
        "args": args,
    }


@pytest.fixture(scope="session")
def report_generator(request: pytest.FixtureRequest) -> TestReportGenerator:
    """Session-scoped test report generator."""
    session = request.session
    if not hasattr(session.config, "_report_generator"):
        setattr(session.config, "_report_generator", TestReportGenerator())
    # Type ignore needed because mypy doesn't know about dynamically added attributes
    return getattr(session.config, "_report_generator")  # type: ignore[attr-defined]


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Generate test report after all tests complete."""
    # Get the report generator from session config if it exists
    if hasattr(session.config, "_report_generator"):
        report_gen: TestReportGenerator = session.config._report_generator
        if report_gen.results:
            report_path = report_gen.generate_report()
            print(f"\n{'=' * 80}")
            print(f"📊 Test Report Generated: {report_path}")
            print(f"{'=' * 80}\n")
