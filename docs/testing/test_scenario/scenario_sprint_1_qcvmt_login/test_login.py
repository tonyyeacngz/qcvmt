"""
QCVMT Login E2E Tests
Module: login
Generated from Sprint 1 - QCVMT Login test plan.
"""
import pytest
from playwright.sync_api import expect, Page

BASE_URL = "http://alb-te3srjr8fe3bq5gsld.cn-shanghai.alb.aliyuncsslb.com"


# ---------------------------------------------------------------------------
# ID:  BL-25503
# case_name: qcvmt login
# module:  login
# scenario: qcvnt login
# ---------------------------------------------------------------------------
def test_login_module_qcvmt_login_success(page: Page):
    """
    BL-25503 - qcvmt login
    Module: login
    Scenario: qcvnt login
    Priority: P0
    Pre-condition: login qcvmt
    Steps:
      1. Open qcvmt URL -> page opens
      2. Login with email: test@126.com, password: test, qc id qc86
    Expected:
      - Page opens successfully
      - Login succeeds and user lands on home page
    Data Set 1: UserName=admin, Password=123456, QC Number=qc86
    """
    # Step 1: open the application
    page.goto(BASE_URL, wait_until="domcontentloaded")

    # Assert site is accessible
    expect(page).to_have_url(BASE_URL + "/")
    # Verify the home page heading is visible
    expect(page.get_by_role("heading", name="in my opinion.")).to_be_visible()

    # Step 2: navigate to login page
    page.goto(f"{BASE_URL}/user/login", wait_until="domcontentloaded")

    # Assert login page rendered
    login_heading = page.get_by_role("heading", name="Welcome Back!")
    expect(login_heading).to_be_visible()

    email_input = page.get_by_role("textbox", name="Email")
    password_input = page.get_by_role("textbox", name="Password")
    login_button = page.get_by_role("button", name="Login")

    expect(email_input).to_be_visible()
    expect(password_input).to_be_visible()
    expect(login_button).to_be_visible()

    # Fill credentials (dataset: admin / 123456 / qc86 - mapped to test env)
    email_input.fill("test@126.com")
    password_input.fill("test")

    # Submit login
    login_button.click()
    page.wait_for_load_state("domcontentloaded")

    # Assert login success - redirected away from /login to home
    expect(page).not_to_have_url("**/login**")
    expect(page).to_have_url(BASE_URL + "/")
    # Verify home page heading re-appears after login
    expect(page.get_by_role("heading", name="in my opinion.")).to_be_visible()
