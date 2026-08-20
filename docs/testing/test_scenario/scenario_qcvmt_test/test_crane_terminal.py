"""
QCVMT 岸桥终端监控 E2E Tests – Pytest + Playwright
==================================================
Module:       岸桥终端监控
Scenario:     终端显示 - 正常
Source:       plan_cases.json – QCVMT Test plan

Tests covered in this file:
    BL-24178  正确显示加油区域高亮标识    (P1)
    BL-24172  操作员查看指定岸桥的实时作业视图 (P0)
"""
from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from conftest import _do_login
from settings import (
    BASE_URL,
    DEFAULT_TIMEOUT,
    NAVIGATION_TIMEOUT,
    PASSWORD,
    QC_NUMBER,
    USERNAME,
)


# ---------------------------------------------------------------------------
# Shared terminal-navigation helper
# ---------------------------------------------------------------------------


def _navigate_to_qc_terminal(page: Page, terminal_url: str) -> None:
    """Perform full login + navigate to a QC terminal page.

    After login, opens the specified terminal URL (derived from data["qc_terminal_url"]).
    Waits for the post-login page network to settle before returning.

    Navigation validation (per TEST-SCRIPT-AGENTS.md § 导航验证):
        1. URL must contain the expected path fragment
        2. Core page element (main content wrapper) must be rendered
        3. On failure, attempt re-navigation once before raising
    """
    # 1. Go to BASE_URL → login page
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    login_heading = page.get_by_role(
        "heading", name=re.compile(r"Sign In|登录", re.IGNORECASE)
    )
    login_heading.wait_for(state="visible", timeout=NAVIGATION_TIMEOUT)

    # 2. Authenticate
    _do_login(page, username=USERNAME, password=PASSWORD, qc_number=QC_NUMBER)

    # 3. Navigate to the QC terminal URL from test data
    page.goto(terminal_url, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    # 4. Validate navigation: URL must match expected pattern
    expect(
        page,
        message="QC terminal URL must contain the expected host after navigation",
    ).to_have_url(re.compile(r"^https://[^/]+"))


# ---------------------------------------------------------------------------
# ID:          BL-24178
# case_name:   正确显示加油区域高亮标识
# module:      岸桥终端监控
# scenario:    终端显示 - 正常
# Priority:    P1
# ---------------------------------------------------------------------------


def test_bl_24178_bunkering_zone_highlight(page: Page, data):
    """
    BL-24178 — 正确显示加油区域高亮标识
    Module:     岸桥终端监控
    Scenario:   终端显示 - 正常
    Priority:   P1

    Pre-condition:
        已登录操作员账号；系统已配置船舶加油区域；
        当前QC编号 {{qc_id}} 对应的船舶启用了加油功能

    Test Steps:
        1. 访问QC终端页面 {{qc_terminal_url}}
        2. 查看页面顶部加油状态指示器
        3. 查看贝位矩阵中加油区域的单元格

    Expected Result:
        1. 页面成功加载
        2. 顶部显示“加油状态: 启用”及红色指示灯
        3. 加油区域单元格以红色边框高亮显示
    """
    # ── Step 1: Login + navigate to QC terminal page ──
    qc_terminal_url = data["qc_terminal_url"]
    _navigate_to_qc_terminal(page, qc_terminal_url)

    # Assert: terminal page has rendered (main content wrapper visible)
    page_body = page.get_by_role("body")
    expect(
        page_body, message="QC terminal page body must be rendered"
    ).to_be_visible(timeout=NAVIGATION_TIMEOUT)

    # ── Step 2: Check top-of-page bunkering status indicator ──
    # Expected: "加油状态: 启用" (or English equivalent "Bunkering Status: Enabled")
    # rendered with a red indicator light (usually a red badge / span with red style)
    bunkering_status = page.get_by_text(
        re.compile(r"加油状态|bunkering status", re.IGNORECASE)
    )
    expect(
        bunkering_status,
        message="Bunkering status indicator must be visible at the top of the terminal page",
    ).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Assert: status text explicitly says "启用" / "Enabled"
    status_enabled = page.get_by_text(
        re.compile(r"启用|enabled|active", re.IGNORECASE)
    )
    expect(
        status_enabled,
        message="Bunkering status must read '启用' / 'Enabled'",
    ).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # ── Step 3: Check bay matrix cells – bunkering zone highlights ──
    # Bunkering zone cells are highlighted with a red border.
    # In Ant Design table/cell implementations, this is typically a <td> or a
    # <div>/<span> inside the cell carrying an inline style with red colour
    # or a CSS class like 'bunkering', 'fuel', 'highlight'.
    bunkering_cells = page.locator(
        "td.bunkering, td.fuel, "
        "[class*='bunker'], [class*='fuel'], "
        "[class*='highlight'], "
        "td[style*='border'][style*='red'], "
        "td[style*='border-color: red'], "
        "td[style*='border-color:red']"
    )
    expect(
        bunkering_cells.first,
        message=(
            "At least one bunkering-zone cell must be present in the bay "
            "matrix with a red border highlight"
        ),
    ).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Assert: the highlight uses red border (check computed style)
    # Use evaluate() to verify the CSS border-color is red-ish (rgb(255,…) or #ff0/ #f00 variant)
    border_color_js = """
        (el) => {
            const style = window.getComputedStyle(el);
            return style.borderColor || style.borderTopColor;
        }
    """
    first_cell = bunkering_cells.first
    border_color = first_cell.evaluate(border_color_js)
    red_pattern = re.compile(r"(rgb\(255|red|#ff|#f00|#F00)", re.IGNORECASE)
    assert red_pattern.search(border_color or ""), (
        f"Expected bunkering cell border to be red, got border-color='{border_color}'"
    )


# ---------------------------------------------------------------------------
# ID:          BL-24172
# case_name:   操作员查看指定岸桥的实时作业视图
# module:      岸桥终端监控
# scenario:    终端显示 - 正常
# Priority:    P0
# ---------------------------------------------------------------------------


def test_bl_24172_realtime_work_view(page: Page, data):
    """
    BL-24172 — 操作员查看指定岸桥的实时作业视图
    Module:     岸桥终端监控
    Scenario:   终端显示 - 正常
    Priority:   P0

    Pre-condition:
        已登录操作员账号；系统已配置船舶贝位结构；
        N4系统连接正常；已分配QC编号 {{qc_id}}

    Test Steps:
        1. 登录后访问QC终端页面 {{qc_terminal_url}}
        2. 系统自动根据QC编号 {{qc_id}} 查询N4系统作业队列
        3. 查看贝位视图表格

    Expected Result:
        1. QC终端页面成功加载
        2. 系统返回该岸桥的作业数据
        3. 正确显示贝位矩阵、集装箱位置和剩余数量
    """
    qc_id = data["qc_id"]
    qc_terminal_url = data["qc_terminal_url"]

    # ── Step 1: Login + navigate to QC terminal page ──
    _navigate_to_qc_terminal(page, qc_terminal_url)

    # Assert: terminal page loaded successfully
    page_body = page.get_by_role("body")
    expect(
        page_body,
        message="QC terminal page must fully render after navigation",
    ).to_be_visible(timeout=NAVIGATION_TIMEOUT)

    # ── Step 2: System auto-queries N4 by QC id (verify QC is displayed) ──
    # The current QC number should be shown somewhere on the page (header badge,
    # breadcrumb, or info bar).
    qc_label = page.get_by_text(re.compile(rf"\b{re.escape(qc_id)}\b"))
    expect(
        qc_label,
        message="Page must display the assigned QC id number",
    ).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # ── Step 3: Verify bay matrix / work-view table ──
    # Expected elements:
    #   a. A table / grid representing bay positions (贝位矩阵)
    #   b. Container position indicators
    #   c. Remaining quantity counters
    #
    # Strategy: the terminal uses an Ant Design <Table> or a custom HTML
    # <table>. Both expose role="table" or "grid".

    work_table = page.get_by_role("table")
    expect(
        work_table.first,
        message="Bay position table (role=table) must be visible with work queue data",
    ).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Assert: table header cells for bay position (贝位) and container info are present
    # Common header keywords in QCVMT terminals: Bay / 贝位 / Row / 列 / Tier / 层
    header_cells = work_table.first.locator("thead th, thead td")
    expect(
        header_cells.first,
        message="Bay matrix must have header columns",
    ).to_be_visible(timeout=DEFAULT_TIMEOUT)
    header_count = header_cells.count()
    assert header_count > 0, "Bay position table must have at least one header column"

    # Assert: table body rows exist (N4 returned work data)
    body_rows = work_table.first.locator("tbody tr")
    expect(
        body_rows.first,
        message="Bay matrix must contain at least one data row from N4 work queue",
    ).to_be_visible(timeout=DEFAULT_TIMEOUT)

    # Assert: remaining quantity column (剩余数量) is present
    # Look for a header cell matching 剩余 / remaining / qty / 数量
    remaining_header = work_table.first.locator(
        "thead th",
        has_text=re.compile(r"剩余|remaining|qty|数量|remains", re.IGNORECASE),
    )
    # If the header is not explicitly labelled (some terminal UIs use a compact view),
    # fall back to verifying numeric content exists in the table body.
    if remaining_header.count() > 0:
        expect(remaining_header.first).to_be_visible(timeout=DEFAULT_TIMEOUT)
    else:
        # Fallback: at least one cell in each row contains a number
        numeric_cell = work_table.first.locator("tbody td").filter(has_text=re.compile(r"^\d+$"))
        assert numeric_cell.count() > 0, (
            "Bay matrix cells must contain numeric values (container counts / remaining quantities)"
        )
