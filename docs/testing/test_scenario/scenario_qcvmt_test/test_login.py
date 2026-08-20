"""
QCVMT Login E2E Tests – Pytest + Playwright
===========================================
Module:       login
Scenario:     qcvnt login
Source:       plan_cases.json – QCVMT Test plan
"""
from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from conftest import _do_login
from settings import BASE_URL, DEFAULT_TIMEOUT, NAVIGATION_TIMEOUT


# ---------------------------------------------------------------------------
# ID:          BL-25503
# case_name:   qcvmt login
# module:      login
# scenario:    qcvnt login
# Priority:    P0
# ---------------------------------------------------------------------------


def test_bl_25503_qcvmt_login(page: Page, data):
    """
    BL-25503 — qcvmt login
    Module:     login
    Scenario:   qcvnt login
    Priority:   P0

    Pre-condition:
        login qcvmt

    Test Steps:
        1. open https://qcvmt.getsvc.com/
        2. login with user name: admin, password: 123456, qc id QC86

    Expected Result:
        - can be open
        - login success

    Data Set 1:
        - UserName: admin
        - Password: 123456
        - QC Number: 58
    """
    # ── Step 1: Open the application URL (→ auto-redirects to /login) ──
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    # Assert: login page heading is visible ⇒ site can be opened
    login_heading = page.get_by_role(
        "heading",
        name=re.compile(r"Sign In|登录|sign in", re.IGNORECASE),
    )
    expect(
        login_heading,
        message="Login page must render after navigating to BASE_URL",
    ).to_be_visible(timeout=NAVIGATION_TIMEOUT)

    # Assert: all login form inputs are present BEFORE filling
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

    expect(username_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    expect(password_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    expect(qc_number_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    expect(login_button).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # ── Step 2: login with credentials from data set ──
    _do_login(
        page,
        username=data["UserName"],
        password=data["Password"],
        qc_number=data["QC Number"],
    )

    # ── Expected Result assertions ──
    # URL must not contain /login after successful authentication
    expect(
        page,
        message="URL must redirect away from /login after successful login",
    ).not_to_have_url(re.compile(r"/login"))

    # Must land on a valid post-login URL
    expect(
        page,
        message="Must land on a valid post-login page",
    ).to_have_url(re.compile(r"^https://[^/]+(/.*)?$"))

    # Post-login indicator: Logout button should be visible
    logout_button = page.get_by_role(
        "button", name=re.compile(r"logout|注销|退出登录|sign out", re.IGNORECASE)
    )
    expect(
        logout_button,
        message="Logout button (or equivalent) must be visible after login",
    ).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Page title must reflect post-login state
    expect(
        page, message="Page title should NOT match login title after authentication"
    ).not_to_have_title(re.compile(r"^.*[Ll]ogin.*$"))
