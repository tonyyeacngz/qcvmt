"""
QCVMT Login E2E Tests - Pytest + Playwright
Module: login
Scenario: qcvnt login
Source: plan_cases.json - Sprint 1 QCVMT login regression
"""
from __future__ import annotations

import re

from playwright.sync_api import expect, Page

from conftest import _do_login
from settings import BASE_URL, NAVIGATION_TIMEOUT, DEFAULT_TIMEOUT


# ---------------------------------------------------------------------------
# ID: BL-25503
# case_name: qcvmt login
# module: login
# scenario: qcvnt login
# Priority: P0
# ---------------------------------------------------------------------------


def test_bl_25503_qcvmt_login(page: Page, data):
    """
    BL-25503 - qcvmt login
    Module: login
    Scenario: qcvnt login
    Priority: P0

    Pre-condition:
      - login qcvmt

    Test Steps:
      1. open https://qcvmt.getsvc.com/
      2. login with user name: admin, password: 123456, qc id QC86

    Expected Result:
      - can be open
      - login success

    Data Set 1:
      - UserName: admin
      - Password: 123456
      - QC Number: qc86
    """
    # Step 1: Open the application URL
    # Navigate to the base URL - should auto-redirect to /login
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    # Assert: page can be opened - login page rendered
    login_heading = page.get_by_role(
        "heading",
        name=re.compile(r"Sign In|登录|sign in", re.IGNORECASE)
    )
    expect(login_heading).to_be_visible(timeout=NAVIGATION_TIMEOUT)

    # Verify login form elements are present
    username_input = page.get_by_role(
        "textbox",
        name=re.compile(r"username|用户名", re.IGNORECASE)
    )
    password_input = page.get_by_role(
        "textbox",
        name=re.compile(r"password|密码", re.IGNORECASE)
    )
    qc_number_input = page.get_by_role(
        "textbox",
        name=re.compile(r"qc number|qc编号", re.IGNORECASE)
    )
    login_button = page.get_by_role(
        "button",
        name=re.compile(r"login|登录|sign in", re.IGNORECASE)
    )

    expect(username_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    expect(password_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    expect(qc_number_input).to_be_visible(timeout=DEFAULT_TIMEOUT)
    expect(login_button).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Step 2: Login with parameters from data set
    _do_login(
        page,
        username=data["UserName"],
        password=data["Password"],
        qc_number=data["QC Number"],
    )

    # Assert: login success - redirected away from /login
    expect(page, message="Should redirect away from /login after successful login").not_to_have_url(
        re.compile(r"/login")
    )

    # Assert: landed on a valid post-login page (e.g. /terminal, /dashboard, /)
    expect(page, message="Should be on a valid post-login URL").to_have_url(
        re.compile(r"^https://[^/]+(/.*)?$")
    )

    # Assert: post-login page has rendered core elements
    # Check for logout button (common indicator of authenticated state)
    logout_button = page.get_by_role(
        "button",
        name=re.compile(r"logout|注销|退出登录|sign out", re.IGNORECASE)
    )
    expect(
        logout_button,
        message="Logout button should be visible after successful login"
    ).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Additional assertion: page title should not be the login page title
    expect(page, message="Page title should reflect post-login state").not_to_have_title(
        re.compile(r"^.*[Ll]ogin.*$")
    )
