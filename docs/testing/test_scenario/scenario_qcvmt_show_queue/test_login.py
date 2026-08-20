# -*- coding: utf-8 -*-
"""
Test Case: BL-25503
Module: login
Scenario: qcvnt login
Priority: P0
Type: Functional
Case Name: qcvmt login

Pre-conditions:
- login qcvmt

Test Steps:
1. Open https://qcvmt.getsvc.com/
2. Login with user name: admin, password: 123456, qc id QC86

Expected Results:
1. Page can be opened
2. Login success

Data Set:
- UserName: admin
- Password: 123456
- QC Number: qc86

Generated from: plan_cases.json case #1
"""
from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

from conftest import perform_login, TIMEOUT_S, TIMEOUT_M, TIMEOUT_L
from settings import BASE_URL, LOGIN_URL


class TestQcvmtLogin:
    """Test suite for BL-25503: qcvmt login"""

    @pytest.mark.login
    def test_bl_25503_qcvmt_login(self, page: Page, case_data: list[dict]):
        """
        BL-25503: qcvmt login
        Module: login
        Scenario: qcvnt login
        Priority: P0

        Tests the complete login flow:
        1. Opens the application URL
        2. Fills login form with credentials from test data
        3. Verifies successful login and redirect

        Expected Results:
        - Login page loads successfully
        - All form fields are visible and interactable
        - Login succeeds and redirects to main page
        - Logout button is visible (confirms authenticated state)
        """
        # Get test data from case_data fixture
        if not case_data:
            pytest.skip("No test data provided for BL-25503")

        test_data = case_data[0]  # Use first data set

        username = test_data.get("UserName", "admin")
        password = test_data.get("Password", "123456")
        qc_number = test_data.get("QC Number", "86")

        # ======================================================================
        # STEP 1: Navigate to application URL
        # ======================================================================
        page.goto(LOGIN_URL, wait_until="networkidle")

        # Assert: Login page loaded successfully
        login_heading = page.get_by_role("heading", name=re.compile(r"Sign In|登录", re.I))
        expect(login_heading).to_be_visible(timeout=TIMEOUT_M)

        # Assert: Page title is correct
        expect(page).to_have_title(re.compile(r"QCVMT|登录|Login", re.I))

        # Assert: All form fields are present
        # Username field
        username_input = page.get_by_role("textbox", name=re.compile(r"\*?\s*Username|\*?\s*用户名", re.I))
        expect(username_input).to_be_visible(timeout=TIMEOUT_S)

        # Password field
        password_input = page.get_by_role("textbox", name=re.compile(r"\*?\s*Password|\*?\s*密码", re.I))
        expect(password_input).to_be_visible(timeout=TIMEOUT_S)

        # QC Number field
        qc_input = page.get_by_role("textbox", name=re.compile(r"\*?\s*QC Number|\*?\s*QC编号", re.I))
        expect(qc_input).to_be_visible(timeout=TIMEOUT_S)

        # Login button
        login_button = page.get_by_role("button", name=re.compile(r"Login|登录|Sign In", re.I))
        expect(login_button).to_be_visible(timeout=TIMEOUT_S)

        # ======================================================================
        # STEP 2: Perform login with test credentials
        # ======================================================================
        perform_login(page, username, password, qc_number)

        # ======================================================================
        # STEP 3: Verify successful login
        # ======================================================================
        # Assert: URL has changed (redirected from /login)
        expect(page).not_to_have_url(re.compile(r"/login", re.I))

        # Assert: Logout button is visible (indicates authenticated state)
        logout_button = page.get_by_role("button", name=re.compile(r"Logout|注销|Sign Out", re.I))
        expect(logout_button).to_be_visible(timeout=TIMEOUT_M)

        # Assert: User is on a valid authenticated page
        current_url = page.url
        assert current_url.startswith(BASE_URL), f"Expected URL to start with {BASE_URL}, got {current_url}"
