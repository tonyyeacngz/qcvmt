# -*- coding: utf-8 -*-
"""
QCVMT E2E Test Configuration
Generated with real selectors from Playwright MCP exploration
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from settings import (
    BASE_URL,
    LOGIN_URL,
    TERMINAL_URL,
    USERNAME,
    PASSWORD,
    QC_NUMBER,
    TIMEOUT_S,
    TIMEOUT_M,
    TIMEOUT_L,
)

# User agent for tests
USER_AGENT = "QCVMT-E2E-Test-Automation/1.0 (Playwright-Pytest)"


def extract_case_data(func_name: str, test_data: dict) -> list[dict]:
    """
    Extract test data sets for a given test function.
    Function naming: test_<case_id_lowercase>_<description>
    Example: test_bl_25503_qcvmt_login -> case_id = "BL-25503"
    """
    parts = func_name.split("_", 3)
    if len(parts) < 3:
        return []

    prefix_letter = parts[1].upper()
    case_number = parts[2].upper()
    case_id = f"{prefix_letter}-{case_number}"

    datasets = test_data.get(case_id, [])
    if not datasets:
        return []

    return datasets


class TestDataManager:
    """Centralized test data loader with error handling"""

    def __init__(self, data_file: str = "test_data.json"):
        self.data_file = Path(__file__).parent / data_file
        self._cache: dict | None = None

    def load(self) -> dict:
        """Load and cache test data from JSON file"""
        if self._cache is not None:
            return self._cache

        if not self.data_file.exists():
            raise FileNotFoundError(
                f"Test data file not found: {self.data_file}\n"
                f"Ensure test_data.json exists in: {self.data_file.parent}"
            )

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
            return self._cache
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.data_file}: {e}")

    def get_case_data(self, case_id: str) -> list[dict]:
        """Get all data sets for a specific case ID"""
        data = self.load()
        datasets = data.get(case_id, [])
        if not datasets:
            raise ValueError(
                f"No data sets found for case_id: {case_id}\n"
                f"Available case_ids: {list(data.keys())}"
            )
        return datasets


# Global data manager instance
data_manager = TestDataManager()


def pytest_configure(config):
    """Register custom pytest marks"""
    config.addinivalue_line("markers", "login: mark test as a login test")
    config.addinivalue_line("markers", "terminal_monitor: mark test as terminal monitor test")


@pytest.fixture(scope="session")
def test_data() -> dict:
    """Session-scoped test data fixture"""
    return data_manager.load()


@pytest.fixture(scope="function")
def case_data(request: pytest.FixtureRequest, test_data: dict) -> list[dict]:
    """
    Function-scoped fixture to extract case data based on test method name.
    Test methods must follow: test_<case_id_lowercase>_<description>
    """
    # Get the test method name from the request
    func_name = getattr(request.node, "originalname", None) or request.node.name
    return extract_case_data(func_name, test_data)


@pytest.fixture(scope="session")
def browser_instance() -> Browser:
    """
    Session-scoped browser instance.
    Configured with:
    - Headless mode
    - Custom user agent
    - Viewport size 1280x720
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )
        yield browser
        browser.close()


@pytest.fixture
def context(browser_instance: Browser) -> BrowserContext:
    """
    Test-scoped browser context with tracing enabled.
    Creates isolated context for each test with:
    - Trace recording
    - Screenshot on failure
    - Custom viewport and user agent
    """
    context = browser_instance.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent=USER_AGENT,
        record_video_dir="videos/",
        record_video_size={"width": 1280, "height": 720},
    )

    # Start tracing for all actions
    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True,
    )

    yield context

    # Stop tracing and save
    context.tracing.stop()
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Test-scoped page fixture"""
    page = context.new_page()
    page.set_default_timeout(TIMEOUT_M)
    yield page
    page.close()


def perform_login(page: Page, username: str, password: str, qc_number: str):
    """
    Perform login operation using real selectors extracted from MCP exploration.

    Selectors source: Playwright MCP browser_snapshot and browser_click operations

    Args:
        page: Playwright Page instance
        username: Login username
        password: Login password
        qc_number: QC Number (numeric, will strip 'qc'/'QC' prefix if present)
    """
    import re
    from playwright.sync_api import expect

    # Navigate to login page
    page.goto(LOGIN_URL, wait_until="networkidle")

    # Wait for login form to be visible
    login_heading = page.get_by_role("heading", name=re.compile(r"Sign In|登录", re.I))
    login_heading.wait_for(state="visible", timeout=TIMEOUT_M)

    # Fill Username field
    # Selector: get_by_role("textbox", name="* Username")
    username_input = page.get_by_role("textbox", name=re.compile(r"\*?\s*Username|\*?\s*用户名", re.I))
    username_input.scroll_into_view_if_needed()
    username_input.wait_for(state="visible", timeout=TIMEOUT_S)
    username_input.fill(username)

    # Fill Password field
    # Selector: get_by_role("textbox", name="* Password")
    password_input = page.get_by_role("textbox", name=re.compile(r"\*?\s*Password|\*?\s*密码", re.I))
    password_input.scroll_into_view_if_needed()
    password_input.wait_for(state="visible", timeout=TIMEOUT_S)
    password_input.fill(password)

    # Fill QC Number field
    # Selector: get_by_role("textbox", name="* QC Number")
    # Note: Page renders "QC" as fixed prefix, so we strip it from input
    qc_input = page.get_by_role("textbox", name=re.compile(r"\*?\s*QC Number|\*?\s*QC编号|\*?\s*QC 编号", re.I))
    qc_input.scroll_into_view_if_needed()
    qc_input.wait_for(state="visible", timeout=TIMEOUT_S)

    # Strip 'QC' or 'qc' prefix if present
    clean_qc = re.sub(r"^(qc|QC)\s*", "", qc_number).strip()
    qc_input.fill(clean_qc)

    # Click Login button
    # Selector: get_by_role("button", name="Login")
    login_button = page.get_by_role("button", name=re.compile(r"Login|登录|Sign In", re.I))
    login_button.scroll_into_view_if_needed()
    expect(login_button).to_be_visible(timeout=TIMEOUT_S)
    login_button.click()

    # Wait for navigation away from login page
    page.wait_for_url(
        re.compile(r"^(?!.*login).*"),
        timeout=TIMEOUT_L,
    )
    page.wait_for_load_state("networkidle")
