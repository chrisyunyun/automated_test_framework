"""
易威行 OA 系统 — 导航功能测试
用例来源: LOGIN-FT-011 及后续非登录相关的功能用例

测试地址: https://192.168.16.4:8900/#/login
"""
import pytest
from playwright.sync_api import Page

from pages.oa_login_page import OALoginPage
from config import config

VALID_ACCOUNT  = config.OA_ACCOUNT
VALID_PASSWORD = config.OA_PASSWORD


class TestOANavigation:
    """OA 导航功能测试集"""

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-011  首页快捷入口 → 产品管理
    # ────────────────────────────────────────────────────────────
    @pytest.mark.smoke
    def test_ft011_quick_entry_product_management(self, browser):
        """LOGIN-FT-011: 首页点击快捷入口→产品管理，应正确跳转到产品管理页面"""
        ctx = browser.new_context(ignore_https_errors=True)
        page = ctx.new_page()
        lp = OALoginPage(page)

        # 步骤 1：登录成功
        lp.navigate()
        lp.login(VALID_ACCOUNT, VALID_PASSWORD)
        lp.wait_login_success()

        # 步骤 2：点击快捷入口中的「产品管理」
        page.locator('.quickItem', has_text='产品管理').click()

        # 步骤 3：等待页面跳转到产品管理路由
        page.wait_for_url('**/good/product/proMangement', timeout=8000)
        page.wait_for_load_state('networkidle', timeout=5000)

        # 断言 1：URL 包含产品管理路由
        assert '/good/product/proMangement' in page.url, \
            f"应跳转到产品管理页面，实际 URL: {page.url!r}"

        # 断言 2：左侧菜单「产品管理」处于选中态
        active_menu = page.locator('.el-menu-item.is-active', has_text='产品管理')
        assert active_menu.is_visible(), \
            "左侧菜单「产品管理」应处于选中状态"

        ctx.close()
    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-012  产品管理 — 搜索「潘多拉」，期望有结果
    # ────────────────────────────────────────────────────────────
    @pytest.mark.smoke
    def test_ft012_product_search_with_results(self, browser):
        """LOGIN-FT-012: 产品管理搜索品名「潘多拉」，应能查询出结果"""
        ctx = browser.new_context(ignore_https_errors=True)
        page = ctx.new_page()
        lp = OALoginPage(page)

        # 步骤 1：登录成功，进入产品管理
        lp.navigate()
        lp.login(VALID_ACCOUNT, VALID_PASSWORD)
        lp.wait_login_success()
        page.locator('.quickItem', has_text='产品管理').click()
        page.wait_for_url('**/good/product/proMangement', timeout=8000)
        page.wait_for_load_state('networkidle', timeout=5000)
        page.wait_for_timeout(800)

        # 步骤 2：搜索品名「潘多拉」
        page.locator('input[placeholder="请输入"]').fill('潘多拉')
        page.locator('button', has_text='搜索').click()
        page.wait_for_load_state('networkidle', timeout=5000)
        page.wait_for_timeout(1000)

        # 断言 1：表格有数据行
        rows = page.query_selector_all('.el-table__row')
        assert len(rows) > 0, f"品名「潘多拉」应有查询结果，实际行数: 0"

        # 断言 2：列表中包含品名「潘多拉」
        names = [row.query_selector_all('td')[1].text_content().strip() for row in rows]
        assert '潘多拉' in names, f"结果列表中应包含「潘多拉」，实际: {names}"

        ctx.close()

    # ────────────────────────────────────────────────────────────
    # LOGIN-FT-013  产品管理 — 搜索「比翼双飞」，期望无结果
    # ────────────────────────────────────────────────────────────
    @pytest.mark.smoke
    def test_ft013_product_search_no_results(self, browser):
        """LOGIN-FT-013: 产品管理搜索品名「比翼双飞」，应查询无结果"""
        ctx = browser.new_context(ignore_https_errors=True)
        page = ctx.new_page()
        lp = OALoginPage(page)

        # 步骤 1：登录成功，进入产品管理
        lp.navigate()
        lp.login(VALID_ACCOUNT, VALID_PASSWORD)
        lp.wait_login_success()
        page.locator('.quickItem', has_text='产品管理').click()
        page.wait_for_url('**/good/product/proMangement', timeout=8000)
        page.wait_for_load_state('networkidle', timeout=5000)
        page.wait_for_timeout(800)

        # 步骤 2：搜索品名「比翼双飞」
        page.locator('input[placeholder="请输入"]').fill('比翼双飞')
        page.locator('button', has_text='搜索').click()
        page.wait_for_load_state('networkidle', timeout=5000)
        page.wait_for_timeout(1000)

        # 断言：表格无数据行（无结果）
        rows = page.query_selector_all('.el-table__row')
        assert len(rows) == 0, f"品名「比翼双飞」应无结果，实际行数: {len(rows)}"

        ctx.close()

