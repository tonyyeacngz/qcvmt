"""
QCVMT E2E Tests – Pytest + Playwright
=====================================
Module: scenario_qcvmt_test (login + 岸桥终端监控)
Source:   plan_cases.json – QCVMT Test plan
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
from playwright.sync_api import expect

from settings import (
    ASSERTION_TIMEOUT,
    BASE_URL,
    DEFAULT_TIMEOUT,
    NAVIGATION_TIMEOUT,
    PASSWORD,
    QC_NUMBER,
    USERNAME,
)


# ---------------------------------------------------------------------------
# Test-data loader
# ---------------------------------------------------------------------------

DATA_FILE = Path(__file__).parent / "test_data.json"
_DATA_CACHE: Optional[Dict[str, List[Dict[str, Any]]]] = None


class TestDataFileNotFoundError(Exception):
    """Raised when test_data.json cannot be located."""


class TestDataMissingFieldError(Exception):
    """Raised when a required data field is absent from test_data.json."""


def _load_data_file() -> Dict[str, List[Dict[str, Any]]]:
    """Load and cache test_data.json; raise clearly if missing."""
    global _DATA_CACHE
    if _DATA_CACHE is not None:
        return _DATA_CACHE

    if not DATA_FILE.exists():
        raise TestDataFileNotFoundError(
            f"Test data file not found: {DATA_FILE}. "
            "Ensure test_data.json exists in the script directory."
        )

    with DATA_FILE.open("r", encoding="utf-8") as fh:
        _DATA_CACHE = json.load(fh)
    return _DATA_CACHE


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Inject ``data`` parameter into test functions that declare it.

    - Declares ``data`` → look up case_id in test_data.json → parametrise.
    - No entry for case_id → skip with a clear message.
    - Does NOT declare ``data`` → no injection.
    """
    if "data" not in metafunc.fixturenames:
        return

    func_name = metafunc.function.__name__
    case_id = _extract_case_id(func_name)
    if case_id is None:
        return

    try:
        all_data = _load_data_file()
    except TestDataFileNotFoundError as exc:
        pytest.skip(str(exc))
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
        ids.append(str(ds.get("set_name", "default")))
        params.append(ds)

    metafunc.parametrize("data", params, ids=ids)


def _extract_case_id(func_name: str) -> Optional[str]:
    """Convert ``test_bl_25503_*`` → ``BL-25503`` (canonical upper-hyphen)."""
    m = re.match(r"test_([a-z]+_\d+)(?:_.+)?$", func_name)
    if not m:
        return None
    prefix_id = m.group(1)          # e.g. bl_25503
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
    """Apply trace=on-first-retry, video, timeouts per TEST-SCRIPT-AGENTS.md."""
    return {
        **browser_context_args,
        "record_video_dir": str(Path(__file__).parent / "videos"),
        "record_video_size": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="session")
def context(browser, browser_context_args):
    ctx = browser.new_context(**browser_context_args)
    # Trace on-first-retry: start tracing unconditionally so retries are captured
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    ctx.set_default_timeout(DEFAULT_TIMEOUT)
    ctx.set_default_navigation_timeout(NAVIGATION_TIMEOUT)
    yield ctx
    ctx.close()


@pytest.fixture
def page(context):
    p = context.new_page()
    yield p
    p.close()


# ---------------------------------------------------------------------------
# Login helper – shared across modules
# ---------------------------------------------------------------------------


def _do_login(page, username: str, password: str, qc_number: str) -> None:
    """Fill login form and wait for post-login navigation.

    - Username / Password / QC Number inputs are located via role + i18n regex.
    - The page renders a fixed 'QC' prefix outside the QC Number input,
      so any leading 'QC' / 'qc' is stripped before filling.
    """
    username_input = page.get_by_role(
        "textbox", name=re.compile(r"username|用户名", re.IGNORECASE)
    )
    password_input = page.get_by_role(
        "textbox", name=re.compile(r"password|密码", re.IGNORECASE)
    )
    qc_number_input = page.get_by_role(
        "textbox", name=re.compile(r"qc number|qc编号|qc 编号", re.IGNORECASE)
    )
    login_button = page.get_by_role(
        "button", name=re.compile(r"login|登录|sign in", re.IGNORECASE)
    )

    # Username
    username_input.scroll_into_view_if_needed()
    expect(username_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    username_input.fill(username)

    # Password
    password_input.scroll_into_view_if_needed()
    expect(password_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    password_input.fill(password)

    # QC Number – strip leading QC/qc prefix
    qc_number_input.scroll_into_view_if_needed()
    expect(qc_number_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    qc_value = re.sub(r"^(qc|QC)", "", qc_number).strip()
    qc_number_input.fill(qc_value)

    # Submit
    login_button.scroll_into_view_if_needed()
    expect(login_button).to_be_visible(timeout=DEFAULT_TIMEOUT)
    login_button.click()

    # Wait for navigation away from /login
    page.wait_for_url(
        re.compile(r"^(?!.*login).*"),
        timeout=NAVIGATION_TIMEOUT,
    )
    page.wait_for_load_state("networkidle")


@pytest.fixture
def logged_in_page(page):
    """Full login flow using default credentials from settings.py."""
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    # Verify login page rendered before filling
    login_heading = page.get_by_role(
        "heading", name=re.compile(r"Sign In|登录", re.IGNORECASE)
    )
    login_heading.wait_for(state="visible", timeout=NAVIGATION_TIMEOUT)

    _do_login(page, username=USERNAME, password=PASSWORD, qc_number=QC_NUMBER)
    return page


# ---------------------------------------------------------------------------
# Screenshot / trace hook – capture on BOTH pass and fail
# ---------------------------------------------------------------------------


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

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
        # Page may already be closed – ignore
        pass
