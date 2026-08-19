"""
QCVMT Login E2E Tests - Pytest + Playwright
Module: login
Scenario: qcvnt login
Source: plan_cases.json - Sprint 1 QCVMT login regression
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from settings import (
    ASSERTION_TIMEOUT,
    BASE_URL,
    DEFAULT_TIMEOUT,
    NAVIGATION_TIMEOUT,
    PASSWORD,
    QC_NUMBER,
    USERNAME,
)


DATA_FILE = Path(__file__).parent / "test_data.json"
_DATA_CACHE: Optional[Dict[str, List[Dict[str, Any]]]] = None


class TestDataFileNotFoundError(Exception):
    """Raised when the test_data.json file cannot be located."""


class TestDataMissingFieldError(Exception):
    """Raised when a required data field declared by a test is absent
    from test_data.json configuration."""


def _load_data_file() -> Dict[str, List[Dict[str, Any]]]:
    """Load and cache test_data.json. Raises a custom error if file missing."""
    global _DATA_CACHE
    if _DATA_CACHE is not None:
        return _DATA_CACHE

    if not DATA_FILE.exists():
        raise TestDataFileNotFoundError(
            f"Test data file not found: {DATA_FILE}. "
            "Please ensure test_data.json exists in the script directory."
        )

    with DATA_FILE.open("r", encoding="utf-8") as f:
        _DATA_CACHE = json.load(f)
    return _DATA_CACHE


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Inject `data` parameter to test functions that declare it.

    - If the test method declares a `data` parameter, look up its test_case_id
      in test_data.json and parametrize across all data sets.
    - If test_data.json does not contain the case_id, skip with a clear message.
    - If the test method does NOT declare `data`, skip injection.
    """
    if "data" not in metafunc.fixturenames:
        return

    # Extract test_case_id from the test function name: test_{case_id}_...
    func_name = metafunc.function.__name__
    # Convention: test_{case_id}_{description}  e.g. test_bl_25503_qcvmt_login
    case_id = _extract_case_id(func_name)
    if case_id is None:
        return

    try:
        all_data = _load_data_file()
    except TestDataFileNotFoundError as e:
        pytest.skip(str(e))
        return

    datasets = all_data.get(case_id)
    if not datasets:
        pytest.skip(
            f"No data_set configured in test_data.json for case_id={case_id}"
        )
        return

    ids: List[str] = []
    params: List[Dict[str, Any]] = []
    for ds in datasets:
        set_name = str(ds.get("set_name", "default"))
        ids.append(set_name)
        params.append(ds)

    metafunc.parametrize("data", params, ids=ids)


def _extract_case_id(func_name: str) -> Optional[str]:
    """Extract the canonical test_case_id (e.g. BL-25503) from the test
    function name. Function names use lowercased, hyphen-to-underscore form:
    test_bl_25503_... -> BL-25503.
    """
    m = re.match(r"test_([a-z]+_\d+)_(.+)$", func_name)
    if not m:
        return None
    prefix_id = m.group(1)  # e.g. bl_25503
    # Convert back to canonical form: BL-25503
    parts = prefix_id.split("_", 1)
    if len(parts) != 2:
        return None
    prefix, num = parts
    return f"{prefix.upper()}-{num}"


# ---------------------------------------------------------------------------
# Browser / context fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure trace, video, timeouts per TEST-SCRIPT-AGENTS.md spec."""
    return {
        **browser_context_args,
        "record_video_dir": str(Path(__file__).parent / "videos"),
        "record_video_size": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="session")
def context(browser, browser_context_args):
    context = browser.new_context(**browser_context_args)
    # Trace on-first-retry: start tracing unconditionally so retries produce traces
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(DEFAULT_TIMEOUT)
    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT)
    yield context
    context.close()


@pytest.fixture
def page(context, request):
    """Per-test page fixture with trace-on-first-retry semantics."""
    page = context.new_page()
    yield page
    page.close()


# ---------------------------------------------------------------------------
# Login fixture - performs the full login flow once per test
# ---------------------------------------------------------------------------


@pytest.fixture
def logged_in_page(page):
    """Navigate to the login page, fill credentials, submit, and wait for
    redirection off /login. Returns the authenticated page object.
    """
    # Step 1: navigate to the application root -> auto-redirects to /login
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    # Validate we arrived at the login page
    expect_login_page = page.get_by_role("heading", name=re.compile(r"Sign In|登录"))
    expect_login_page.wait_for(state="visible", timeout=NAVIGATION_TIMEOUT)

    return page


def _do_login(page, username: str, password: str, qc_number: str) -> None:
    """Shared login routine:

    - Fill Username, Password, QC Number (stripping any 'QC' / 'qc' prefix
      because the page renders a fixed 'QC' prefix outside the input)
    - Click Login button
    - Wait for navigation off /login
    """
    from playwright.sync_api import expect as _expect

    # Locate inputs using role + label (robust to language variations)
    username_input = page.get_by_role(
        "textbox",
        name=re.compile(r"username|用户名", re.IGNORECASE),
    )
    password_input = page.get_by_role(
        "textbox",
        name=re.compile(r"password|密码", re.IGNORECASE),
    )
    qc_number_input = page.get_by_role(
        "textbox",
        name=re.compile(r"qc number|qc编号|qc 编号", re.IGNORECASE),
    )
    login_button = page.get_by_role(
        "button",
        name=re.compile(r"login|登录|sign in", re.IGNORECASE),
    )

    # Username
    username_input.scroll_into_view_if_needed()
    _expect(username_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    username_input.fill(username)

    # Password
    password_input.scroll_into_view_if_needed()
    _expect(password_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    password_input.fill(password)

    # QC Number - strip leading QC/qc prefix (page renders "QC" as fixed prefix)
    qc_number_input.scroll_into_view_if_needed()
    _expect(qc_number_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    qc_value = re.sub(r"^(qc|QC)", "", qc_number).strip()
    qc_number_input.fill(qc_value)

    # Login button
    login_button.scroll_into_view_if_needed()
    _expect(login_button).to_be_visible(timeout=DEFAULT_TIMEOUT)
    login_button.click()

    # Wait for navigation off /login
    page.wait_for_url(
        re.compile(r"^(?!.*login).*"),
        timeout=NAVIGATION_TIMEOUT,
    )
    page.wait_for_load_state("networkidle")


# ---------------------------------------------------------------------------
# Screenshot / trace hook - capture evidence on both success and failure
# ---------------------------------------------------------------------------


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    # Locate page fixture on the request
    page = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
    if page is None:
        return

    screenshots_dir = Path(__file__).parent / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    safe_nodeid = re.sub(r"[^\w\-.]+", "_", item.nodeid)
    status = "pass" if report.passed else "fail"

    screenshot_path = screenshots_dir / f"{safe_nodeid}_{status}.png"

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception:
        # Page may already be closed - ignore screenshot errors
        pass


# ---------------------------------------------------------------------------
# Helper wrappers to keep test files lean
# ---------------------------------------------------------------------------


def expect_visible(locator):
    """Convenience wrapper - asserts that locator is visible."""
    from playwright.sync_api import expect
    return expect(locator)
